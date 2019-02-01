#include <pybind11/pybind11.h>
//#include <winrt/Windows.Devices.Bluetooth.h>
#include <winrt/base.h>

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
        py::list devices;
        py::dict bogusDevice;
        bogusDevice["name"] = "SK-Bogus";
        bogusDevice["address"] = "FF:FF:FF:FF:FF";
        devices.append(bogusDevice);
        return devices;
    }
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

