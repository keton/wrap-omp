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

## Minimalistic
No containers, package definition scripts or other hard to configure stuff. If project builds on host it will build in sandbox.

Just a read only copy of your system intended to prevent agent from installing packages and changing settings it should not.

# Usage
## Installation
- copy wrap-omp to your executable path. For example `cp wrap-omp ~/.local/bin`
- copy config template and adapt it for your needs: `cp wrap-omp.conf.template ~/.config/wrap-omp.conf`

## Running
In your project folder do `wrap-omp <any omp arguments>`

oh-my-pi will function as usual provided required API keys have been passed in config file.