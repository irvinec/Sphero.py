#include <pybind11/pybind11.h>
#include <winrt/Windows.Devices.Bluetooth.h>
#include <winrt/Windows.Devices.Enumeration.h>

// Link to umbrella lib.
#pragma comment(lib, "windowsapp")

using namespace winrt;
namespace py = pybind11;

struct WinBleAdapter
{
    WinBleAdapter()
    {
        init_apartment();
    }

    ~WinBleAdapter()
    {
        uninit_apartment();
    }

    void Start()
    {

    }

    py::list Scan()
    {
        // Query for extra properties you want returned
        std::vector<std::string> requestedProperties = { "System.Devices.Aep.DeviceAddress", "System.Devices.Aep.IsConnected" };

        Windows::Devices::Enumeration::DeviceWatcher deviceWatcher =
            Winodws::Devices::Enumeration::DeviceInformation::CreateWatcher(
                    Winodws::Devices::Bluetooth::BluetoothLEDevice::GetDeviceSelectorFromPairingState(false),
                    requestedProperties,
                    Winodws::Devices::Enumeration::DeviceInformationKind::AssociationEndpoint);

        // Register event handlers before starting the watcher.
        // Added, Updated and Removed are required to get all nearby devices
        //deviceWatcher.Added += DeviceWatcher_Added;
        //deviceWatcher.Updated += DeviceWatcher_Updated;
        //deviceWatcher.Removed += DeviceWatcher_Removed;

        // EnumerationCompleted and Stopped are optional to implement.
        //deviceWatcher.EnumerationCompleted += DeviceWatcher_EnumerationCompleted;
        //deviceWatcher.Stopped += DeviceWatcher_Stopped;

        // Start the watcher.
        deviceWatcher.Start();

        py::list devices;
        py::dict bogusDevice;
        bogusDevice["name"] = "SK-Bogus";
        bogusDevice["address"] = "FF:FF:FF:FF:FF";
        devices.append(bogusDevice);
        return devices;
    }

private:

};

PYBIND11_MODULE(winble, m)
{
    py::class_<WinBleAdapter>(m, "WinBleAdapter")
        .def(py::init<>())
        .def("start", &WinBleAdapter::Start)
        .def("scan", &WinBleAdapter::Scan);

    m.doc() = "Windows BLE Library";

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}

