from distutils.core import setup
import py2exe

# setup(console=[{"script":"iflow.py"}])


INCLUDES = ['pyreadline']
options = {"py2exe":
               {
                    "compressed": 1,
                    "optimize": 2,
                    "includes": INCLUDES,
                    "dll_excludes": ["OLEAUT32.dll", "USER32.dll", "SHELL32.dll",
                                     "ole32.dll", "ADVAPI32.dll", "WS2_32.dll", "GDI32.dll", "VERSION.dll", "KERNEL32.dll"]
               }
}
setup(options = options, zipfile=None,console=[{"script": "iflow.py", "icon_resources": [(1, "logo.ico")] }])
