%define rspamd_user      _rspamd
%define rspamd_group     %{rspamd_user}
%define rspamd_home      %{_localstatedir}/lib/rspamd
%define rspamd_logdir    %{_localstatedir}/log/rspamd
%define rspamd_confdir   %{_sysconfdir}/rspamd
%define rspamd_pluginsdir   %{_datadir}/rspamd
%define rspamd_rulesdir   %{_datadir}/rspamd/rules
%define rspamd_wwwdir   %{_datadir}/rspamd/www

Name:           rspamd
Version:        1.0.2
Release: 1
Summary:        Rapid spam filtering system
Group:          System Environment/Daemons

# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
%if 0%{?suse_version}
License:        BSD-2-Clause
%else
License:        BSD2c
%endif
URL:            https://rspamd.com
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}
BuildRequires:  glib2-devel,libevent-devel,openssl-devel,pcre-devel,perl
BuildRequires:  cmake,gmime
%if 0%{?suse_version} || 0%{?el7} || 0%{?fedora}
BuildRequires:  systemd
Requires(pre):  systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif
%if 0%{?suse_version}
BuildRequires:  sqlite3-devel
Requires(pre):  shadow
%else
BuildRequires:  sqlite-devel
Requires(pre):  shadow-utils
%endif
%if 0%{?fedora_version} >= 22 || 0%{?suse_version} >= 1320
BuildRequires:  luajit-devel,hiredis-devel
%else
BuildRequires:  lua-devel
%endif
%if 0%{?el6}
Requires:       logrotate
Requires(post): chkconfig
Requires(preun): chkconfig, initscripts
Requires(postun): initscripts
Source1:        %{name}.init
Source2:        %{name}.logrotate
%endif

Source0:        https://rspamd.com/downloads/%{name}-%{version}.tar.xz
Patch0:         %{name}.service.patch

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%setup -q
%if 0%{?el7}
%patch0 -p0
%endif

%build
%{__cmake} \
		-DCMAKE_C_OPT_FLAGS="%{optflags}" \
        -DCMAKE_INSTALL_PREFIX=%{_prefix} \
        -DCONFDIR=%{_sysconfdir}/rspamd \
        -DMANDIR=%{_mandir} \
        -DDBDIR=%{_localstatedir}/lib/rspamd \
        -DRUNDIR=%{_localstatedir}/run/rspamd \
%if 0%{?el6}
        -DWANT_SYSTEMD_UNITS=OFF \
%else
        -DWANT_SYSTEMD_UNITS=ON \
        -DSYSTEMDDIR=%{_unitdir} \
%endif
%if 0%{?suse_version}
        -DCMAKE_SKIP_INSTALL_RPATH=ON \
%endif
%if 0%{?fedora_version} >= 22 || 0%{?suse_version} >= 1320
		-DENABLE_LUAJIT=ON \
		-DENABLE_HIREDIS=ON \
%else
		-DENABLE_LUAJIT=OFF \
		-DENABLE_HIREDIS=OFF \
%endif
        -DLOGDIR=%{_localstatedir}/log/rspamd \
        -DEXAMPLESDIR=%{_datadir}/examples/rspamd \
        -DPLUGINSDIR=%{_datadir}/rspamd \
        -DLIBDIR=%{_libdir}/rspamd/ \
        -DINCLUDEDIR=%{_includedir} \
        -DNO_SHARED=ON \
        -DDEBIAN_BUILD=1 \
        -DRSPAMD_GROUP=%{rspamd_group} \
        -DRSPAMD_USER=%{rspamd_user}

%{__make} %{?jobs:-j%jobs}

%install
%{__make} install DESTDIR=%{buildroot} INSTALLDIRS=vendor

%if 0%{?el6}
%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
%{__install} -d -p -m 0755 %{buildroot}%{_localstatedir}/run/rspamd
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -d -p -m 0755 %{buildroot}%{rspamd_logdir}
%endif

%{__install} -d -p -m 0755 %{buildroot}%{rspamd_home}

%clean
rm -rf %{buildroot}

%pre
%{_sbindir}/groupadd -r %{rspamd_group} 2>/dev/null || :
%{_sbindir}/useradd -g %{rspamd_group} -c "Rspamd user" -s /bin/false -r -d %{rspamd_home} %{rspamd_user} 2>/dev/null || :

%if 0%{?suse_version}
%service_add_pre %{name}.service
%service_add_pre %{name}.socket
%endif

%post
#to allow easy upgrade from 0.8.1
%{__chown} -R %{rspamd_user}:%{rspamd_group} %{rspamd_home}
%if 0%{?suse_version}
%service_add_post %{name}.service
%service_add_post %{name}.socket
%endif
%if 0%{?fedora} || 0%{?el7}
%systemd_post %{name}.service
%systemd_post %{name}.socket
%endif
%if 0%{?el6}
/sbin/chkconfig --add %{name}
%endif

%preun
%if 0%{?suse_version}
%service_del_preun %{name}.service
%service_del_preun %{name}.socket
%endif
%if 0%{?fedora} || 0%{?el7}
%systemd_preun %{name}.service
%systemd_preun %{name}.socket
%endif
%if 0%{?el6}
if [ $1 = 0 ]; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
%endif

%postun
%if 0%{?suse_version}
%service_del_postun %{name}.service
%service_del_postun %{name}.socket
%endif
%if 0%{?fedora} || 0%{?el7}
%systemd_postun_with_restart %{name}.service
%systemd_postun %{name}.socket
%endif
%if 0%{?el6}
if [ $1 -ge 1 ]; then
    /sbin/service %{name} condrestart > /dev/null 2>&1 || :
fi

%endif

%files
%defattr(-,root,root,-)
%if 0%{?suse_version} || 0%{?fedora} || 0%{?el7}
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.socket
%endif
%if 0%{?el6}
%{_initrddir}/%{name}
%dir %{_localstatedir}/run/rspamd
%endif
%{_mandir}/man8/%{name}.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*
%{_bindir}/rspamd
%{_bindir}/rspamc
%{_bindir}/rspamadm
%config(noreplace) %{rspamd_confdir}/%{name}.conf
%config(noreplace) %{rspamd_confdir}/%{name}.sysvinit.conf
%config(noreplace) %{rspamd_confdir}/composites.conf
%config(noreplace) %{rspamd_confdir}/metrics.conf
%config(noreplace) %{rspamd_confdir}/modules.conf
%config(noreplace) %{rspamd_confdir}/statistic.conf
%config(noreplace) %{rspamd_confdir}/common.conf
%config(noreplace) %{rspamd_confdir}/logging.inc
%config(noreplace) %{rspamd_confdir}/options.inc
%config(noreplace) %{rspamd_confdir}/worker-controller.inc
%config(noreplace) %{rspamd_confdir}/worker-normal.inc
%config(noreplace) %{rspamd_confdir}/modules.d/*
%config(noreplace) %{rspamd_confdir}/rspamd.systemd.conf
%if 0%{?el6}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%endif
%if 0%{?el6}
%dir %{rspamd_logdir}
%endif
%attr(-, _rspamd, _rspamd) %dir %{rspamd_home}
%dir %{rspamd_rulesdir}/regexp
%dir %{rspamd_rulesdir}
%dir %{rspamd_confdir}
%dir %{rspamd_confdir}/modules.d
%dir %{rspamd_pluginsdir}/lua
%dir %{rspamd_pluginsdir}
%dir %{rspamd_wwwdir}
%dir %{_libdir}/rspamd
%config(noreplace) %{rspamd_confdir}/2tld.inc
%config(noreplace) %{rspamd_confdir}/surbl-whitelist.inc
%config(noreplace) %{rspamd_confdir}/spf_dkim_whitelist.inc
%config(noreplace) %{rspamd_confdir}/dmarc_whitelist.inc
%{rspamd_pluginsdir}/lua/forged_recipients.lua
%{rspamd_pluginsdir}/lua/maillist.lua
%{rspamd_pluginsdir}/lua/multimap.lua
%{rspamd_pluginsdir}/lua/once_received.lua
%{rspamd_pluginsdir}/lua/rbl.lua
%{rspamd_pluginsdir}/lua/ratelimit.lua
%{rspamd_pluginsdir}/lua/phishing.lua
%{rspamd_pluginsdir}/lua/trie.lua
%{rspamd_pluginsdir}/lua/emails.lua
%{rspamd_pluginsdir}/lua/ip_score.lua
%{rspamd_pluginsdir}/lua/settings.lua
%{rspamd_pluginsdir}/lua/fun.lua
%{rspamd_pluginsdir}/lua/hfilter.lua
%{rspamd_pluginsdir}/lua/spamassassin.lua
%{rspamd_pluginsdir}/lua/dmarc.lua
%{rspamd_pluginsdir}/lua/whitelist.lua
%{rspamd_rulesdir}/regexp/drugs.lua
%{rspamd_rulesdir}/regexp/fraud.lua
%{rspamd_rulesdir}/regexp/headers.lua
%{rspamd_rulesdir}/regexp/lotto.lua
%{rspamd_rulesdir}/rspamd.lua
%{rspamd_rulesdir}/html.lua
%{rspamd_rulesdir}/misc.lua
%{rspamd_rulesdir}/rspamd.classifiers.lua
%{rspamd_wwwdir}/*
%{_libdir}/rspamd/*
%{_datadir}/rspamd/effective_tld_names.dat

%changelog
* Thu Sep 17 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 1.0.0-1
- Update to 1.0.0

* Fri May 29 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.9-1
- Update to 0.9.9

* Thu May 21 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.4-1
- Update to 0.9.4

* Tue May 19 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.3-1
- Update to 0.9.3

* Tue May 19 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.2-1
- Update to 0.9.2

* Sun May 17 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.1-1
- Update to 0.9.1

* Wed May 13 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.0-1
- Update to 0.9.0

* Fri Mar 13 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.8.3-1
- Update to 0.8.3

* Tue Mar 10 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.8.2-1
- Update to 0.8.2

* Fri Jan 23 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.8.1-1
- Update to 0.8.1

* Fri Jan 02 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.8.0-1
- Update to 0.8.0

* Mon Nov 24 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.6-1
- Update to 0.7.6

* Mon Nov 17 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.5-1
- Update to 0.7.5

* Sat Nov 08 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.4-1
- Update to 0.7.4

* Mon Nov 03 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.3-1
- Update to 0.7.3

* Wed Oct 15 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.2-1
- Update to 0.7.2

* Tue Sep 30 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.1-1
- Update to 0.7.1

* Mon Sep 1 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.0-1
- Update to 0.7.0

* Fri Jan 10 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.7-1
- Update to 0.6.7.

* Fri Dec 27 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.6-1
- Update to 0.6.6.

* Fri Dec 20 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.5-1
- Update to 0.6.5.

* Wed Dec 18 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.4-1
- Update to 0.6.4.

* Tue Dec 10 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.3-1
- Update to 0.6.3.

* Fri Dec 06 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.2-1
- Update to 0.6.2.

* Tue Nov 19 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.0-1
- Update to 0.6.0.

* Mon Jun 10 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.5.6-1
- Update to 0.5.6.

* Sat May 25 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.5.5-1
- Initial spec version.
