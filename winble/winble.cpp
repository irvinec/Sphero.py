#include <pybind11/pybind11.h>
#include <unordered_set>
#include <condition_variable>
#include <chrono>
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
        // Query for extra properties you want returned
        std::vector<hstring> requestedProperties
        {
            L"System.Devices.Aep.DeviceAddress",
            L"System.Devices.Aep.IsConnected",
            L"System.Devices.Aep.Bluetooth.Le.AddressType"
        };

        // TODO: move much of this into start instead.
        m_deviceWatcher =
            Windows::Devices::Enumeration::DeviceInformation::CreateWatcher(
                //Windows::Devices::Bluetooth::BluetoothLEDevice::GetDeviceSelectorFromPairingState(false),
                Windows::Devices::Bluetooth::BluetoothLEDevice::GetDeviceSelectorFromConnectionStatus(Windows::Devices::Bluetooth::BluetoothConnectionStatus::Disconnected),
                requestedProperties,
                Windows::Devices::Enumeration::DeviceInformationKind::AssociationEndpoint
            );

        // Register event handlers before starting the watcher.
        // Added, Updated and Removed are required to get all nearby devices
        m_addedEventToken = m_deviceWatcher.Added(
            [this](
                const Windows::Devices::Enumeration::DeviceWatcher&,
                const Windows::Devices::Enumeration::DeviceInformation& deviceInfo
            )
            {
                m_nearbyDevices.insert(deviceInfo);
            }
        );

        m_updatedEventToken = m_deviceWatcher.Updated(
            [this](
                const Windows::Devices::Enumeration::DeviceWatcher&,
                const Windows::Devices::Enumeration::DeviceInformationUpdate& deviceInfoUpdate
            )
            {
                auto foundDeviceInfo = std::find_if(m_nearbyDevices.cbegin(), m_nearbyDevices.cend(),
                    [&deviceInfoUpdate](
                        const Windows::Devices::Enumeration::DeviceInformation& deviceInfo
                    ) -> bool
                    {
                        return deviceInfo.Id() == deviceInfoUpdate.Id();
                    }
                );

                if (foundDeviceInfo != m_nearbyDevices.cend())
                {
                    foundDeviceInfo->Update(deviceInfoUpdate);
                }
            }
        );

        m_removedEventToken = m_deviceWatcher.Removed(
            [this](
                const Windows::Devices::Enumeration::DeviceWatcher&,
                const Windows::Devices::Enumeration::DeviceInformationUpdate& deviceInfoUpdate
            )
            {
                std::remove_if(m_nearbyDevices.begin(), m_nearbyDevices.end(),
                    [&deviceInfoUpdate](
                        const Windows::Devices::Enumeration::DeviceInformation& deviceInfo
                    ) -> bool
                    {
                        return deviceInfo.Id() == deviceInfoUpdate.Id();
                    }
                );
            }
        );

        // EnumerationCompleted and Stopped are optional to implement.
        m_deviceEunumerationCompletedEventToken = m_deviceWatcher.EnumerationCompleted(
            [this](
                const Windows::Devices::Enumeration::DeviceWatcher& deviceWatcher,
                const Windows::Foundation::IInspectable&
            )
            {
                // TODO: we won't stop here
                //deviceWatcher.Stop();
                m_enumerationCompletedEvent.notify_all();
            }
        );

        // Start the watcher.
        m_deviceWatcher.Start();
    }

    py::list Scan()
    {
        // Wait for device enumeration to complete.
        std::mutex m;
        std::unique_lock<std::mutex> lock{ m };
        /*auto now = std::chrono::system_clock::now();
        using namespace std::chrono_literals;
        enumerationCompletedEvent.wait_until(lock, now + 20s);*/
        m_enumerationCompletedEvent.wait(lock);

        // TODO: lock for m_nearbyDevices
        py::list devices;
        for (const auto& deviceInfo : m_nearbyDevices)
        {
            py::dict device;
            device["name"] = to_string(deviceInfo.Name());
            hstring address{ unbox_value<hstring>(deviceInfo.Properties().Lookup(L"System.Devices.Aep.DeviceAddress")) };
            device["address"] = to_string(address);
            devices.append(device);
        }

        return devices;
    }

private:
    Windows::Devices::Enumeration::DeviceWatcher m_deviceWatcher;
    std::unordered_set<Windows::Devices::Enumeration::DeviceInformation> m_nearbyDevices;
    std::condition_variable m_enumerationCompletedEvent;
    event_token m_addedEventToken;
    event_token m_updatedEventToken;
    event_token m_removedEventToken;
    event_token m_deviceEunumerationCompletedEventToken;
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

