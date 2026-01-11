# Just a simple local chat system

Before using, you need to create some directory: `groups`, `userData`, `votes`.
And there must be `public.grp`, `public.dat` under `groups`, and `public.vot` under `votes`.

`encrypt.py` has been hidden, so you have to create it with a function `encrypt(orig: str, ext: str) -> str` in it.

If you want to use `dev_helper.py`, make sure you have default configure file for the program to read.

Of course, you can run `setup.py` to create all these files to get a quick start. **Note that the default encrypt
function is very simple, which means you should change it into your own encrypting algorithm at once.**

It should be used with the project chatClient.
