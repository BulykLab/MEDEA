if command -v wget >/dev/null ; then
	echo "wget found."
else
	echo "wget was not found on your system. Please install it."
fi

if command -v awk >/dev/null ; then
	echo "awk found."
else
	echo "awk was not found on your system. Please install it."
fi

if command -v sed >/dev/null ; then
	echo "sed found."
else
	echo "sed was not found on your system. Please install it."
fi

if command -v python >/dev/null ; then	
	echo "python found."
	PYVER=$(python -c "import sys; print(sys.version_info[0])")
	if [ "$PYVER" != "2" ] ; then echo "This software was written in python 2 and is not guaranteed to work in python 3." ; fi
	if [ -f data/requirements/pythonImports.txt ] ; then
		echo "Verifying all python packages needed are installed."
		while read p; do EX="import $p"; python -c "$EX" >/dev/null 2>&1 ; if [ $? == 1 ]; then echo "   $p not installed"; fi; done <data/requirements/pythonImports.txt
	else
		echo "Couldn't verify all python packages needed are installed."
	fi
else
	echo "python was not found on your system. Please install it."
fi

if command -v intersectBed >/dev/null ; then
	echo "BEDtools subprogram found."
else
	echo "BEDtools was not found on your system. Please install it."
fi

if command -v sqlite3 >/dev/null ; then
	echo "sqlite3 found."
else
	echo "sqlite3 was not found on your system. Please install it."
fi

if command -v Rscript >/dev/null ; then
	echo "R found."
	if [ -f data/requirements/Rlibs.txt ] ; then
		echo "Verifying all R libraries needed are installed."
		while read p; do EX="library($p)"; Rscript -e "$EX" >/dev/null 2>&1 ; if [ $? == 1 ]; then echo "   $p not installed" ; fi ; done <data/requirements/Rlibs.txt
	else
		echo "Couldn't verify all R libraries needed are installed."
	fi
else
	echo "R was not found on your system. Please install it."
fi


