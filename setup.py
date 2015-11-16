from setuptools import setup

setup(
    name="supervisor_event_exec",
    version="0.0.1",
    py_modules=["supervisor_event_exec"],
    install_requires=["supervisor"],
    entry_points="[console_scripts]\nsupervisor-event-exec = supervisor_event_exec:main"
)
