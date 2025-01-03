from setuptools import setup

APP = ['life_os_mahir_timerapp.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter', 'pandas', 'json'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
