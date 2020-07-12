"use strict";
const URL_PARAMS_RE = /^\/(r|user)\/(\w+)\/(?:(?:comments\/)(\w+)\/(?:(?:\w+\/)(\w+)\/?)?)?/,
	MAX_BROADCAST_NOTIFICATIONS = 3,
	truncatePnsByType = (t, e) => (n) => {
		n.filter((e) => e.data.message_type === t)
			.slice(0, -e)
			.forEach((t) => t.close());
	},
	truncateBroadcastFollowerPns = truncatePnsByType("broadcast_follower", 3),
	truncateBroadcastRecommendationPns = truncatePnsByType("broadcast_recommendation", 3);
self.addEventListener("install", (t) => t.waitUntil(self.skipWaiting())),
	self.addEventListener("activate", (t) => {
		t.waitUntil(
			(async () => {
				await self.clients.claim(), await sendCommandToAllClients(t, "registerWithServiceWorker", {});
			})()
		);
	});
const V2_EVENT_BOILER_PLATE_KEY = "v2_event_boiler_plate",
	clientIdToClientData = {},
	cleanseClientData = async () => {
		const t = await self.clients.matchAll({ includeUncontrolled: !0, type: "window" }),
			e = new Set(t.filter((t) => !!t).map((t) => t.id)),
			n = Object.keys(clientIdToClientData);
		for (const t of n) e.has(t) || delete clientIdToClientData[t];
	},
	registerClient = (t) => {
		const e = t.source.id;
		clientIdToClientData[e] = {};
		const {
			data: { v2EventBoilerPlate: n }
		} = t;
		void 0 !== n && idbKeyval.set("v2_event_boiler_plate", JSON.stringify(n)),
			t.waitUntil(processQueuedCommands()),
			t.waitUntil(cleanseClientData());
	},
	pushBadgeCountSyncToClients = async (t, e) => {
		await self.clients.claim(), await sendCommandToAllClients(t, "badgeCountSync", e);
	},
	badgeCountSync = (t) => {
		const { badgeCounts: e } = t.data;
		pushBadgeCountSyncToClients(t, e), t.waitUntil(pushBadgeCountSyncToClients(t, e));
	};
self.addEventListener("message", (t) => {
	const {
		data: { command: e }
	} = t;
	"registerClient" === e
		? registerClient(t)
		: "badgeCountSync" === e
		? badgeCountSync(t)
		: "sendV2Event" === e && sendV2Event(t.data.payload);
});
const sendCommandToAllClients = async (t, e, n) => {
	const i = await self.clients.matchAll({ includeUncontrolled: !0, type: "window" });
	for (let t = 0; t < i.length; t++) {
		const o = i[t];
		o && o.postMessage({ command: e, ...n });
	}
};
let queuedCommands = [];
const processQueuedCommands = async () => {
		if (0 === queuedCommands.length) return;
		const t = (await self.clients.matchAll({ includeUncontrolled: !0, type: "window" })).find(
			(t) => !!t && t.id in clientIdToClientData
		);
		if (t) {
			for (const e of queuedCommands) t.postMessage(e);
			queuedCommands = [];
		}
	},
	extractDataFromDeeplink = (t) => {
		const e = {},
			{ pathname: n } = new URL(t);
		if (!n) return e;
		const i = n.match(URL_PARAMS_RE);
		if (!i) return e;
		const [o, a, s, r] = i.slice(1);
		return (
			a && "r" === o && (e.subreddit = { name: a }),
			s && (e.post = { id: `t3_${s}` }),
			r && (e.comment = { id: `t1_${r}` }),
			e
		);
	},
	logInteraction = async (t, e, n) => {
		let i;
		const o = await idbKeyval.get("v2_event_boiler_plate");
		if ((void 0 !== o && (i = JSON.parse(o)), void 0 === i)) return;
		const a = new Date().toISOString();
		(i.action = e),
			void 0 === i.notification && (i.notification = {}),
			(i.notification.id = n.correlation_id),
			(i.notification.type = n.message_type),
			(i.correlationId = n.correlation_id),
			(i.timestamp = a),
			void 0 === i.platform && (i.platform = {}),
			(i.platform.device_id = n.device_id),
			(i = { ...i, ...extractDataFromDeeplink(n.link) }),
			await sendV2Event(i);
	},
	sendV2Event = async (t) => {
		const e = {
			headers: { "Content-Type": "application/json" },
			method: "POST",
			body: JSON.stringify({ events: [t] })
		};
		try {
			await fetch("/", e);
		} catch (t) {
			console.error(t);
		}
	};
self.addEventListener("push", (t) => {
	const e = t.data.json(),
		n = e.title,
		i = e.options;
	i.icon || (i.icon = "https://www.redditstatic.com/desktop2x/img/favicon/android-icon-192x192.png"),
		t.waitUntil(logInteraction(0, "receive", i.data));
	const o = i.data.auto_dismiss_options;
	void 0 !== o ? "device_default" !== o.behavior && (i.requireInteraction = !0) : (i.requireInteraction = !1),
		t.waitUntil(
			self.registration
				.showNotification(n, i)
				.then(() => self.registration.getNotifications())
				.then((t) => {
					if (
						(truncateBroadcastFollowerPns(t),
						truncateBroadcastRecommendationPns(t),
						void 0 === o || "timed" !== o.behavior)
					)
						return;
					let n;
					for (let i = 0; i < t.length; i++)
						if (t[i].data.correlationId === e.correlationId) {
							if (void 0 === (n = t[i])) continue;
							setTimeout(n.close.bind(n), o.dismiss_time_ms);
						}
				})
		);
}),
	self.addEventListener("notificationclick", (t) => {
		t.notification.close();
		const e = t.notification.data.link;
		t.waitUntil(logInteraction(0, "click", t.notification.data)),
			t.waitUntil(
				clients.matchAll({ type: "window" }).then((t) => {
					for (let n = 0; n < t.length; n++) {
						const i = t[n];
						if (i.url === e && "focus" in i) return i.focus();
					}
					if (clients.openWindow)
						try {
							return clients.openWindow(e);
						} catch (t) {
							console.error(t);
						}
				})
			);
	}),
	self.addEventListener("notificationclose", (t) => {
		t.waitUntil(logInteraction(0, "close", t.notification.data));
	});
var idbKeyval = (function (t) {
	class e {
		constructor(t = "keyval-store", e = "keyval") {
			(this.storeName = e),
				(this._dbp = new Promise((n, i) => {
					const o = indexedDB.open(t, 1);
					(o.onerror = () => i(o.error)),
						(o.onsuccess = () => n(o.result)),
						(o.onupgradeneeded = () => {
							o.result.createObjectStore(e);
						});
				}));
		}
		_withIDBStore(t, e) {
			return this._dbp.then(
				(n) =>
					new Promise((i, o) => {
						const a = n.transaction(this.storeName, t);
						(a.oncomplete = () => i()),
							(a.onabort = a.onerror = () => o(a.error)),
							e(a.objectStore(this.storeName));
					})
			);
		}
	}
	let n;
	function i() {
		return n || (n = new e()), n;
	}
	return (
		(t.Store = e),
		(t.get = function (t, e = i()) {
			let n;
			return e
				._withIDBStore("readonly", (e) => {
					n = e.get(t);
				})
				.then(() => n.result);
		}),
		(t.set = function (t, e, n = i()) {
			return n._withIDBStore("readwrite", (n) => {
				n.put(e, t);
			});
		}),
		(t.del = function (t, e = i()) {
			return e._withIDBStore("readwrite", (e) => {
				e.delete(t);
			});
		}),
		(t.clear = function (t = i()) {
			return t._withIDBStore("readwrite", (t) => {
				t.clear();
			});
		}),
		(t.keys = function (t = i()) {
			const e = [];
			return t
				._withIDBStore("readonly", (t) => {
					(t.openKeyCursor || t.openCursor).call(t).onsuccess = function () {
						this.result && (e.push(this.result.key), this.result.continue());
					};
				})
				.then(() => e);
		}),
		t
	);
})({});
self.addEventListener("fetch", () => {});
