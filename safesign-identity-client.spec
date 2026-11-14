Name:           safesign-identity-client
Version:        4.7.0.0
Release:        1%{?dist}
Summary:        SafeSign Identity Client - Gerenciador de Token Criptográfico (G+D)
License:        Proprietary
URL:            https://gdamericadosul.com.br
ExclusiveArch:  x86_64

# ZIP oficial para RHEL 10; normaliza o nome antes da fase de preparação.
Source0:        SafeSign_IC_Standard_Linux_redhat10_%{version}-AET.000.zip
Source1:        safesign.module
NoSource:       0

# Preserva os binários proprietários pré-compilados.
%global debug_package %{nil}
%global _build_id_links none
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_static_archive %{nil}
%global __brp_strip_lto %{nil}

BuildRequires:  unzip
BuildRequires:  tar
BuildRequires:  gzip
BuildRequires:  desktop-file-utils

# Dependências ELF são geradas automaticamente pelo RPM.
Requires:       pcsc-lite
Requires:       p11-kit
Recommends:     pcsc-tools
Recommends:     opensc

Obsoletes:      SafeSign_Identity_Client < %{version}
Provides:       SafeSign_Identity_Client = %{version}

%description
Utilitário de administração e bibliotecas PKCS#11 para tokens SafeSign,
reempacotado para Fedora a partir dos binários oficiais para Red Hat 10.

%prep
# Aceita o ZIP com o nome original do fabricante.
if [ ! -f "%{SOURCE0}" ]; then
    mv "%{_sourcedir}/SafeSign IC Standard Linux redhat10 %{version}-AET.000.zip" "%{SOURCE0}"
fi
%setup -q -c -T
unzip -p "%{SOURCE0}" rpm_sources.tar.gz > rpm_sources.tar.gz
tar -xzf rpm_sources.tar.gz
test -d BUILD/usr

%build
# Binários pré-compilados.

%install
mkdir -p %{buildroot}/usr
cp -a BUILD/usr/. %{buildroot}/usr/

test -x %{buildroot}%{_bindir}/tokenadmin
test -e %{buildroot}%{_libdir}/libaetpkss.so

install -Dpm0644 %{SOURCE1} \
    %{buildroot}%{_datadir}/p11-kit/modules/safesign.module

desktop-file-validate \
    %{buildroot}%{_datadir}/applications/com.aeteurope.tokenadmin.desktop

# Preserva os caminhos não convencionais das traduções do fabricante.
: > tokenutils.lang
for mo in %{buildroot}%{_datadir}/locale/*/tokenutils.mo; do
    test -f "$mo" || exit 1
    langdir=$(dirname "$mo")
    lang=$(basename "$langdir")
    printf '%%%%lang(%%s) %%s\n' "$lang" "${mo#%{buildroot}}" >> tokenutils.lang
done

%files -f tokenutils.lang
%{_bindir}/tokenadmin
%{_libdir}/libaet*.so*
%{_datadir}/p11-kit/modules/safesign.module
%{_datadir}/applications/com.aeteurope.tokenadmin.desktop
%{_datadir}/metainfo/com.aeteurope.tokenadmin.metainfo.xml
%dir %{_datadir}/doc/safesignidentityclient
%license %{_datadir}/doc/safesignidentityclient/license.txt
%license %{_datadir}/doc/safesignidentityclient/copyright
%license %{_datadir}/doc/safesignidentityclient/SafeSign_License_Agreement_PT_BR.txt
%license %{_datadir}/doc/safesignidentityclient/3rdparty/
%{_mandir}/man1/tokenadmin.1*
%{_datadir}/icons/hicolor/*/apps/tokenadmin.png
%{_datadir}/safesign/

%changelog
* Sat Nov 14 2026 Moacyr Prado <10207086+mwprado@users.noreply.github.com> - 4.7.0.0-1
- Atualiza para SafeSign 4.7.0.0 e utiliza rpm_sources.tar.gz do ZIP oficial.
- Preserva os binários, links simbólicos e integração PKCS#11 com p11-kit.
- Reativa a geração automática de dependências ELF e valida o desktop.
- Identifica traduções e licenças e restringe a arquitetura a x86_64.

* Sun May 17 2026 Moacyr Prado <10207086+mwprado@users.noreply.github.com> - 4.6.0.0-5
- Registra o módulo PKCS#11 do SafeSign no p11-kit.
- Adiciona p11-kit como dependência de execução.
- Adiciona pcsc-tools e opensc como recomendações para diagnóstico.

* Sun May 17 2026 Moacyr Prado <10207086+mwprado@users.noreply.github.com> - 4.6.0.0-1
- Versão inicial portátil obtendo o ZIP diretamente do servidor da G+D América do Sul.
