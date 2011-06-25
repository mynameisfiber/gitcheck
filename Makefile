growl-python: growl/Growl.py growl/__init__.py growl/growlImage.m growl/libgrowl.c
	cd Growl/;python setup.py build_ext --inplace; cd ../

