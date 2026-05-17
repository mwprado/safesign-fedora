Name:           safesign-identity-client
Version:        4.6.0.0
Release:        4%{?dist}
Summary:        SafeSign Identity Client - Gerenciador de Token Criptográfico (G+D)
License:        Proprietaria
URL:            https://gdamericadosul.com.br
# URL de referência para download manual:
# "https://gdamericadosul.com.br/content/SafeSign IC Standard Linux redhat10 4.6.0.0-AET.000.zip"

Source0:        SafeSign_IC_Standard_Linux_redhat10_4.6.0.0-AET.000.zip
NoSource:       0

# Desativa recursos de compilação automáticos que corrompem binários prontos
%define debug_package %{nil}
%define _build_id_links none
%undefine __find_requires
%define __find_requires %{nil}

%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%define _unpackaged_files_terminate_build 0

# Ferramentas necessárias para manipular o ZIP e o RPM interno durante o build
BuildRequires:  unzip
BuildRequires:  rpm-build
BuildRequires:  cpio

# Dependências nativas de execução mapeadas para o ecossistema do Fedora
Requires: glibc >= 2.38
Requires: openssl-libs >= 3.4.0
Requires: libstdc++
Requires: pcsc-lite
Requires: pcsc-lite-libs
Requires: gtk3
Requires: cairo
Requires: pango
Requires: libX11
Requires: gdbm

%description
Utilitário de administração e bibliotecas PKCS#11 para tokens SafeSign,
reempacotado de forma automatizada e portátil para o Fedora a partir do 
binário oficial homologado para Red Hat 10.

%prep
# %setup -q -c -T cria o diretório baseado em Name-Version e entra nele
%setup -q -c -T
unzip -q "%{SOURCE0}"

%build
# Fase vazia (binários pré-compilados)

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# Entra no buildroot para extração limpa
cd %{buildroot}

# Localiza o arquivo .rpm do Red Hat dentro da pasta de build e extrai via cpio
RPM_FILE=$(find %{_builddir}/%{name}-%{version} -name "*.rpm" | head -n 1)
if [ -z "$RPM_FILE" ]; then
    echo "Erro: RPM interno não encontrado no arquivo ZIP!"
    exit 1
fi

rpm2cpio "$RPM_FILE" | cpio -idmv

%post
/sbin/ldconfig
/usr/bin/update-desktop-database &> /dev/null || :
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :

%postun
/sbin/ldconfig
/usr/bin/update-desktop-database &> /dev/null || :
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :

%files
# Mapeamento genérico e seguro de toda a árvore extraída do pacote oficial
%{_bindir}/tokenadmin
%{_libdir}/libaet*.so*
%{_datadir}/applications/*.desktop
%{_datadir}/metainfo/*.xml
%{_datadir}/doc/safesignidentityclient/
%{_mandir}/man1/tokenadmin.1.gz
%{_datadir}/icons/hicolor/*/apps/tokenadmin.png
%{_datadir}/safesign/
%{_datadir}/locale/*/tokenutils.mo

%changelog
* Sun May 17 2026 Seu Nome <seuemail@provedor.com> - 4.6.0.0-1
- Versão inicial portátil obtendo o ZIP diretamente do servidor da G+D América do Sul.
