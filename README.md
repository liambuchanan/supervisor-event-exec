In the unlikely event anyone is using this, please see [supervisor-event-listeners](https://github.com/PlotWatt/supervisor-event-listeners).

# supervisor-event-exec

Execute arbitrary commands on supervisor events and restart processes on non-zero exit status if desired.

Use cases:
* Taking action when an event such as a process restart occurs.
* Monitoring system statistics and restarting processes in certain circumstances.

## Usage
```shell
$ supervisor-event-exec --help
usage: supervisor-event-exec [-h] -e COMMAND [-p [PROGRAM [PROGRAM ...]]] [-a]

optional arguments:
  -h, --help            show this help message and exit
  -e COMMAND, --execute COMMAND
                        Command or script to execute on supervisor events.
  -p [PROGRAM [PROGRAM ...]], --restart-programs [PROGRAM [PROGRAM ...]]
                        Supervisor process name/s to be restarted on non-zero
                        exit status if in RUNNING state.
  -a, --restart-any-program
                        Restart any supervisor processes in RUNNING state on
                        non-zero exit status.
```

### Restart all supervisor processes on non-zero exit status
```yaml
[eventlistener:supervisor-event-exec_restart-all]
command=supervisor-event-exec -e "exit 1" -a
events=TICK_60
```

### Restart specified supervisor process on non-zero exit status
```yaml
[eventlistener:supervisor-event-exec_restart-process]
command=supervisor-event-exec -e "exit 1" -p process_1
events=TICK_60
```

### Touch a file when any supervisor process moves to the stopping state
```yaml
[eventlistener:supervisor-event-exec_touch-file]
command=supervisor-event-exec -e "touch ~/status_file"
events=PROCESS_STATE_STOPPING
```
