# blinkpie
A simple webserver for Arduino IOT

## Prerequisite
A SSL certificate is needed to run the server. Run the following code to generate the certificate file (filename used in this example: `server.pem`):

```
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
```


_Note for Windows Users:_

`openssl` is not installed on Windows by default. However, [Git for Windows](https://gitforwindows.org/), [MSYS2](https://www.msys2.org/), etc distribute pre-compiled openssl binaries which can be used to generate the certificate.

## Usage

To start the server:
```powershell
blinkpie_ser --path "/path/to/ssl_cert"
```

To start the serial handler:
```powershell
blinkpie_hdl --port COM2
```

To display help message:
```powershell
blinkpie_ser --help
blinkpie_hdl --help
```

## Related Projects
- GUI: https://github.com/jamestansx/blinkpie-gui
- Arduino library: https://github.com/jamestansx/blinkpie-arduino
