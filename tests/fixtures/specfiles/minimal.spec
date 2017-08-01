%{?scl:%scl_package test}
%{!?scl:%global pkg_name %{name}}

Name:       %{?scl_prefix}test
Version:    1.0
Release:    1%{?dist}
Summary:    Minimal spec for testing purposes

Group:      Development/Testing
License:    MIT
URL:        http://test.example.com

%description
A minimal SPEC file for testing of RPM packaging.

%prep

%build

%install

%files

%changelog
* Thu Jun 22 2017 Jan Stanek <jstanek@redhat.com> 1.0-1
- Initial package
