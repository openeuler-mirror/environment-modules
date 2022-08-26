%define debug_package %{nil}

Name:             environment-modules
Version:          4.2.5
Release:          2
Summary:          Provides dynamic modification of a user's environment
License:          GPLv2+
URL:              http://modules.sourceforge.net/
Source0:          http://downloads.sourceforge.net/modules/modules-%{version}.tar.bz2

Patch0001:        0001-test-deps6.patch

BuildRequires:    gcc tcl-devel libX11-devel dejagnu sed procps hostname man less
Requires:         tcl sed procps man less
Requires(post):   %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
Provides:         environment(modules)

%description
The Modules package is a tool that simplify shell initialization and lets users easily modify
their environment during the session with modulefiles.

Each modulefile contains the information needed to configure the shell for an application.
Once the Modules package is initialized, the environment can be modified on a per-module basis
using the module command which interprets modulefiles. Typically modulefiles instruct the module
command to alter or set shell environment variables such as PATH, MANPATH, etc. modulefiles may be
shared by many users on a system and users may have their own collection to supplement or replace
the shared modulefiles.

Modules can be loaded and unloaded dynamically and atomically, in an clean fashion. All popular shells
are supported, including bash, ksh, zsh, sh, csh, tcsh, fish, as well as some scripting languages such
as tcl, perl, python, ruby, cmake and r.

Modules are useful in managing different versions of applications. Modules can also be bundled into
metamodules that will load an entire suite of different applications.

%package  help
Summary:  Help document for Environment Modules
Requires: environment-modules = %{version}-%{release}

%description help
Help document for the Environment Modules package.

%prep
%autosetup -n modules-%{version} -p1

%build
%configure --prefix=%{_datadir}/Modules --bindir=%{_datadir}/Modules/bin      \
           --libexecdir=%{_datadir}/Modules/libexec                           \
           --disable-compat-version  --enable-dotmodulespath                  \
           --docdir=%{_docdir}/%{name} --with-quarantine-vars=LD_LIBRARY_PATH \
           --with-modulepath=%{_datadir}/Modules/modulefiles:%{_sysconfdir}/modulefiles:%{_datadir}/modulefiles
%make_build

%install
%make_install

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/{modulefiles,profile.d}
mkdir -p $RPM_BUILD_ROOT%{_datadir}/modulefiles
mkdir -p $RPM_BUILD_ROOT%{_bindir}

touch $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/modules.{csh,sh}
touch $RPM_BUILD_ROOT%{_bindir}/modulecmd
rm -f $RPM_BUILD_ROOT%{_datadir}/Modules/bin/modulecmd
mv    $RPM_BUILD_ROOT%{_datadir}/Modules/bin/envml $RPM_BUILD_ROOT%{_bindir}/
mv    $RPM_BUILD_ROOT%{_mandir}/man1/module{,-c}.1
mv    $RPM_BUILD_ROOT%{_mandir}/man4/modulefile{,-c}.4

rm -f $RPM_BUILD_ROOT%{_docdir}/%{name}/*

install -D -p -m 644 contrib/rpm/macros.%{name} $RPM_BUILD_ROOT/%{_rpmconfigdir}/macros.d/macros.%{name}
install -p contrib/scripts/createmodule{.sh,.py} $RPM_BUILD_ROOT%{_datadir}/Modules/bin
sed -i -e 1s,/usr/bin/python,/usr/bin/python3,  $RPM_BUILD_ROOT%{_datadir}/Modules/bin/createmodule.py

%check
make test

%post
[ ! -L %{_mandir}/man1/module.1.gz ] && rm -f %{_mandir}/man1/module.1.gz
[ ! -L %{_mandir}/man4/modulefile.4.gz ] && rm -f %{_mandir}/man4/modulefile.4.gz
[ ! -L %{_sysconfdir}/profile.d/modules.sh ] &&  rm -f %{_sysconfdir}/profile.d/modules.sh
[ ! -L %{_sysconfdir}/profile.d/modules.csh ] &&  rm -f %{_sysconfdir}/profile.d/modules.csh
[ ! -L $RPM_BUILD_ROOT%{_bindir}/modulecmd ] &&  rm -f %{_bindir}/modulecmd

if [ "$(readlink /etc/alternatives/modules.sh)" = '%{_datadir}/Modules/init/modules.sh' ]; then
  %{_sbindir}/update-alternatives --remove modules.sh %{_datadir}/Modules/init/modules.sh
fi

%{_sbindir}/update-alternatives \
  --install %{_sysconfdir}/profile.d/modules.sh modules.sh %{_datadir}/Modules/init/profile.sh 40 \
  --slave %{_sysconfdir}/profile.d/modules.csh modules.csh %{_datadir}/Modules/init/profile.csh \
  --slave %{_bindir}/modulecmd modulecmd %{_datadir}/Modules/libexec/modulecmd.tcl \
  --slave %{_mandir}/man1/module.1.gz module.1.gz %{_mandir}/man1/module-c.1.gz \
  --slave %{_mandir}/man4/modulefile.4.gz modulefile.4.gz %{_mandir}/man4/modulefile-c.4.gz

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove modules.sh %{_datadir}/Modules/init/profile.sh
fi

%files
%license COPYING.GPLv2
%{_sysconfdir}/modulefiles
%{_bindir}/envml
%dir %{_datadir}/Modules
%dir %{_datadir}/Modules/libexec
%dir %{_datadir}/Modules/init
%{_datadir}/Modules/bin
%{_datadir}/Modules/libexec/modulecmd.tcl
%{_datadir}/Modules/modulefiles
%{_datadir}/modulefiles
%config(noreplace) %{_datadir}/Modules/init/*
%config(noreplace) %{_datadir}/Modules/init/.modulespath
%{_rpmconfigdir}/macros.d/macros.%{name}
%ghost %{_sysconfdir}/profile.d/modules.csh
%ghost %{_sysconfdir}/profile.d/modules.sh
%ghost %{_bindir}/modulecmd

%files help
%doc ChangeLog README doc/build/{NEWS.txt,MIGRATING.txt,diff_v3_v4.txt} doc/example.txt
%ghost %{_mandir}/man1/module.1.gz
%ghost %{_mandir}/man4/modulefile.4.gz
%{_mandir}/man1/module-c.1.gz
%{_mandir}/man4/modulefile-c.4.gz

%changelog
* Thu Aug 25 2022 zoulin <zoulin13@h-partners.com> - 4.2.5-2
- Modify changelog format
- Fix test 375-deps6.exp

* Mon Aug 31 2020 wuchaochao <wuchaochao4@huawei.com> - 4.2.5-1
- Update package version to 4.2.5

* Wed Jan 15 2020 openEuler Buildteam <buildteam@openeuler.org> - 4.1.4-3
- Delete unneeded build requires

* Tue Nov 05 2019 Lijin Yang <yanglijin@huawei.com> - 4.1.4-2
- Init package
