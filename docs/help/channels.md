## Channels

MagicBot responds to `/invite`s sent to him. If you invite him to a channel with a password (`+k` channel mode) he will record the key and use it in the future. If you change the key and he sees you doing it, he'll update his records to use the new key in future.

### +k channels with no /invite bypass

Some networks do not allow `/invite`d users to bypass channel passwords - thus MagicBot can't join without a key and then record the key. There's two things you can do to fix this.

> /msg &lt;bot> config channel:#channel key &lt;password here>

or

> /msg &lt;bot> raw JOIN #channel :&lt;password here>

After using either of these to get MagicBot initially in to a cha