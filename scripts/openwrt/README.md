# Home Assistant router monitoring

`home-assistant-monitoring.json` grants read-only access to the CPU statistics
and ath10k hwmon files used by the installed OpenWrt integration. The paths are
specific to this router. It adds no shell execution or write permissions.

Installed on the router at `/usr/share/rpcd/acl.d/home-assistant-monitoring.json`.
Its existing root login uses `list read '*'`, so this additional ACL group is
already selected. A different login must explicitly select the group.

After verifying that the destination does not contain unrelated configuration,
deploy the file over the existing SSH connection and reload rpcd:

```sh
ssh root@192.168.1.1 'cat > /usr/share/rpcd/acl.d/home-assistant-monitoring.json' < scripts/openwrt/home-assistant-monitoring.json
ssh root@192.168.1.1 '/etc/init.d/rpcd reload'
```

The router's `rpcd.@rpcd[0].timeout` is set to 300 seconds, previously 30.
The shorter lifetime collided with the integration's 30-second polling and
produced expired-session permission failures. Reload the Home Assistant
OpenWrt integration after changing router sessions. Verify live CPU and
temperature sensor updates across multiple polling cycles.

To roll back this change, remove only this added ACL file, restore timeout 30
with `uci set rpcd.@rpcd[0].timeout=30` and `uci commit rpcd`, reload rpcd, and
reload the integration. This reintroduces the denied statistics reads and
short session lifetime.
