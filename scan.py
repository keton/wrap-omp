import asyncio, os, socket

from bleak import BleakScanner


async def main():
    print("pid1:", open("/proc/1/comm").read().strip(), "uid:", os.getuid())
    print("DBUS_SYSTEM_BUS_ADDRESS =", os.environ.get("DBUS_SYSTEM_BUS_ADDRESS"))
    print("real bus socket visible:", os.path.exists("/run/dbus/system_bus_socket"))
    sock = os.environ.get("DBUS_SYSTEM_BUS_ADDRESS", "unix:path=/nonexistent")[len("unix:path="):]
    print("proxy socket exists:", os.path.exists(sock))
    devices = await BleakScanner.discover(timeout=5.0)
    for d in devices:
        print(f"{d.address}  {d.name}")
    print("count:", len(devices))


asyncio.run(main())
