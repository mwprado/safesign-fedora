# SafeSign Identity Client para Fedora

Este repositório contém arquivos de empacotamento e instruções para gerar localmente um pacote RPM do **SafeSign Identity Client 4.6.0.0** para Fedora.

O objetivo é facilitar o uso do SafeSign no Fedora Workstation e em variantes atômicas baseadas em `rpm-ostree`, como Fedora Silverblue e Fedora Kinoite, a partir do instalador originalmente distribuído para Red Hat Enterprise Linux 10.

> [!IMPORTANT]
> Este repositório **não distribui** o SafeSign Identity Client, suas bibliotecas, binários, instaladores ou qualquer outro componente proprietário. O usuário deve obter o instalador original por meios oficiais e observar os termos de licença do fornecedor.

## Finalidade

O SafeSign Identity Client é utilizado para gerenciamento de tokens criptográficos e smart cards usados com certificados digitais, incluindo certificados A3 em tokens USB.

Este projeto se limita a:

- fornecer metadados e scripts de empacotamento RPM;
- documentar o processo de build local;
- documentar a instalação no Fedora;
- registrar o módulo PKCS#11 do SafeSign no `p11-kit`;
- documentar testes básicos com PC/SC, PKCS#11 e Firefox.

## Escopo do repositório

O conteúdo deste repositório cobre apenas os arquivos criados para empacotamento, automação e documentação.

Não fazem parte deste repositório:

- o instalador proprietário do SafeSign;
- bibliotecas como `libaetpkss.so`;
- utilitários proprietários como `tokenadmin`;
- certificados, chaves privadas ou dados de tokens criptográficos.

## Como construir o pacote RPM localmente

Por se tratar de software proprietário, o pacote RPM deve ser gerado localmente pelo usuário, a partir do instalador oficial obtido fora deste repositório.

### 1. Instalar as ferramentas de construção

No Fedora Workstation:

```bash
sudo dnf install fedora-packager rpmdevtools rpm-build unzip cpio
```

### 2. Preparar a árvore RPM

```bash
rpmdev-setuptree
```

Esse comando cria a estrutura padrão em `~/rpmbuild/`, incluindo os diretórios `SPECS`, `SOURCES`, `BUILD`, `RPMS` e `SRPMS`.

### 3. Obter os arquivos necessários

Copie o arquivo de especificação e o módulo `p11-kit` para o diretório `SOURCES`/`SPECS` correspondente:

```bash
cp safesign-identity-client.spec ~/rpmbuild/SPECS/
cp safesign.module ~/rpmbuild/SOURCES/
```

Baixe o instalador oficial do SafeSign Identity Client pelo canal oficial do fornecedor e coloque o arquivo ZIP em `~/rpmbuild/SOURCES/`.

Exemplo, ajustando o nome conforme o arquivo obtido:

```bash
mv "SafeSign IC Standard Linux redhat10 4.6.0.0-AET.000.zip" ~/rpmbuild/SOURCES/SafeSign_IC_Standard_Linux_redhat10_4.6.0.0-AET.000.zip
```

### 4. Construir o pacote

```bash
cd ~/rpmbuild/SPECS/
rpmbuild -bb safesign-identity-client.spec
```

O RPM gerado ficará em:

```text
~/rpmbuild/RPMS/x86_64/
```

## Instalação no Fedora

### Fedora Workstation

Instale os componentes PC/SC e ferramentas recomendadas para diagnóstico:

```bash
sudo dnf install pcsc-lite pcsc-lite-libs pcsc-tools opensc
```

Habilite o socket do PC/SC:

```bash
sudo systemctl enable --now pcscd.socket
```

O `pcscd.service` é ativado sob demanda pelo socket. Em condições normais, não é necessário habilitar o serviço diretamente.

Depois instale o pacote RPM gerado:

```bash
sudo dnf install ~/rpmbuild/RPMS/x86_64/safesign-identity-client-4.6.0.0-*.rpm
```

### Fedora Silverblue / Kinoite

Em sistemas atômicos, habilite o socket do PC/SC:

```bash
sudo systemctl enable --now pcscd.socket
```

Instale o RPM via `rpm-ostree`:

```bash
rpm-ostree install ~/rpmbuild/RPMS/x86_64/safesign-identity-client-4.6.0.0-*.rpm
```

Depois reinicie o sistema para aplicar a nova camada do sistema operacional.

## Verificação da instalação

### PC/SC

Verifique se o socket do PC/SC está ativo:

```bash
systemctl status pcscd.socket
```

Monitore a comunicação com o token:

```bash
pcsc_scan
```

Saída esperada, com dados sanitizados:

```text
PC/SC device scanner
Scanning present readers...
0: Giesecke & Devrient GmbH StarSign Crypto USB Token 00 00

Reader 0: Giesecke & Devrient GmbH StarSign Crypto USB Token 00 00
  Card state: Card inserted
  ATR: ...
```

### PKCS#11 direto

Verifique se a biblioteca PKCS#11 foi instalada:

```bash
ls -l /usr/lib64/libaetpkss.so*
```

Teste o módulo SafeSign diretamente:

```bash
pkcs11-tool --module /usr/lib64/libaetpkss.so -L
```

Saída esperada, com dados sanitizados:

```text
Available slots:
Slot 0: Giesecke & Devrient GmbH StarSign Crypto USB Token 00 00
  token label        : <NOME DO TITULAR>
  token manufacturer : A.E.T. Europe B.V.
  token model        : <MODELO>
  token flags        : login required, rng, token initialized, PIN initialized
  serial num         : <SERIAL>
```

Para listar objetos e certificados do token:

```bash
pkcs11-tool --module /usr/lib64/libaetpkss.so --login --list-objects
```

### p11-kit

O pacote instala o arquivo:

```text
/usr/share/p11-kit/modules/safesign.module
```

com o conteúdo:

```ini
module: /usr/lib64/libaetpkss.so
```

Verifique se o `p11-kit` reconhece o SafeSign:

```bash
p11-kit list-modules | grep -A20 -i safesign
```

Saída esperada, com dados sanitizados:

```text
module: safesign
    path: /usr/lib64/libaetpkss.so
    library-description: Cryptographic Token Interface
    library-manufacturer: A.E.T. Europe B.V.
    token: <NOME DO TITULAR>
        manufacturer: A.E.T. Europe B.V.
        model: <MODELO>
        serial-number: <SERIAL>
        flags:
              rng
              login-required
              user-pin-initialized
              token-initialized
```

## Configuração do Firefox

Para que o Firefox utilize certificados A3 em token USB, é possível registrar explicitamente o módulo PKCS#11 do SafeSign.

O caminho esperado da biblioteca é:

```text
/usr/lib64/libaetpkss.so
```

### Método 1: política do Firefox

Este método registra o módulo para todos os perfis do Firefox no sistema.

```bash
sudo mkdir -p /etc/firefox/policies
sudo tee /etc/firefox/policies/policies.json >/dev/null <<'EOF'
{
  "policies": {
    "SecurityDevices": {
      "SafeSign PKCS11": "/usr/lib64/libaetpkss.so"
    }
  }
}
EOF
```

Em Fedora Silverblue e Kinoite, `/etc` é mutável, portanto esse método também é aplicável.

### Método 2: configuração manual no Firefox

1. Insira o token criptográfico em uma porta USB.
2. Abra o Firefox.
3. Acesse `about:preferences#privacy`.
4. Vá até a seção **Certificados**.
5. Clique em **Dispositivos de Segurança**.
6. Clique em **Carregar**.
7. Preencha os campos:
   - **Nome do módulo:** `SafeSign PKCS#11 Module`
   - **Nome do arquivo do módulo:** `/usr/lib64/libaetpkss.so`
8. Confirme a operação e verifique se o dispositivo aparece como ativo ou disponível.

Verifique se o Firefox reconheceu a política:

```text
about:policies
```

## Certificados A1

Para certificados A1 em arquivo `.pfx` ou `.p12`, não é necessário registrar o módulo PKCS#11.

No Firefox:

1. Acesse `about:preferences#privacy`.
2. Vá até **Certificados**.
3. Clique em **Ver Certificados**.
4. Na aba **Seus certificados**, clique em **Importar**.
5. Selecione o arquivo `.pfx` ou `.p12`.
6. Informe a senha de proteção do certificado.

## Licença

Os arquivos próprios deste repositório, incluindo documentação e arquivos de empacotamento, são distribuídos sob a licença MIT. Consulte o arquivo [`LICENSE`](LICENSE).

O **SafeSign Identity Client** e seus componentes binários são software proprietário de seus respectivos titulares, incluindo AET Europe B.V. e/ou G+D Mobile Security/G+D América do Sul, conforme o canal de distribuição utilizado. Este repositório não concede direitos sobre esses componentes proprietários.
