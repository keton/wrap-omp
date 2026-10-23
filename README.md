# wrap-omp sandbox for oh-my-pi

This is a simple script to run [oh-my-pi](https://github.com/can1357/oh-my-pi) in [bubblewrap](https://github.com/containers/bubblewrap) sandbox. Provides isolation in case agent hallucinates and starts executing some commands it should not. 

__Note:__ This is __NOT__ a protection against malicious plugins or skills. Hackers are more clever than agents. The fact that various models failed to escape the sandbox in my testing does not mean anything in case of skilled attacker.

## Sandbox boundary
- filesystem is a blank tmpfs with critical folders mounted __read only__
- minimal set of files required for oh-my-pi to function
- only `~/.omp` and workspace folder (`$PWD` by default) are writeable
- when the workspace is `$HOME`, it is mounted read only (`~/.omp` stays writeable)
- host environment variables are not passed to the sandbox

## Configurable
You can edit `~/.config/wrap-omp.conf` to add variables and files passed to the sandbox

D-Bus access is off unless enabled. The `dbus` object starts a filtered
`xdg-dbus-proxy` for the `system` and/or `session` bus and passes the policy
arguments (`--see`, `--talk`, `--own`, `--call`, `--broadcast`) through.

Image clipboard access is off unless `"clipboard_bridge": true`. `wrap-omp`
then starts `omp-clip-broker` on the host and binds only its socket and the
`omp-clip-shim` script into the sandbox (`omp-clip-shim` replaces `wl-paste`).
The broker serves exactly one thing — the current `image/png` from the host
Wayland clipboard, capped at 32 MiB. There is no request protocol, no MIME
argument, no `SET_PNG`, and no clipboard text; the sandbox never gets a Wayland
socket or `XDG_RUNTIME_DIR`. Copying *out* keeps working through OSC 52 in the
terminal. Text paste via `ctrl+v` stays unavailable; use the terminal's own
paste.

The broker socket is `SOCK_SEQPACKET`, so a normal Wayland client
(`SOCK_STREAM`) pointed at it fails at `connect()` with `EPROTOTYPE` and exits
cleanly. Either way the sandbox has no compositor, so the clip directory is not
a Wayland endpoint.

## Minimalistic
No containers, package definition scripts or other hard to configure stuff. If project builds on host it will build in sandbox.

Just a read only copy of your system intended to prevent agent from installing packages and changing settings it should not.

# Usage
## Installation
- copy `wrap-omp`, `omp-clip-shim` and `omp-clip-broker` to your executable
  path. For example `cp wrap-omp omp-clip-shim omp-clip-broker ~/.local/bin`
  (the shim and broker must sit next to `wrap-omp`)
- copy config template and adapt it for your needs: `cp wrap-omp.conf.template ~/.config/wrap-omp.conf`

## Running
In your project folder do `wrap-omp <any omp arguments>`

oh-my-pi will function as usual provided required API keys have been passed in config file.