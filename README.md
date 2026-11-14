# SafeSign Identity Client para Fedora

Este repositório contém arquivos de empacotamento e instruções para gerar localmente um pacote RPM do **SafeSign Identity Client 4.7.0.0** para Fedora.

O objetivo é facilitar o uso do SafeSign no Fedora Workstation e em variantes atômicas baseadas em `rpm-ostree`, como Fedora Silverblue e Fedora Kinoite, a partir do instalador originalmente distribuído para Red Hat Enterprise Linux 10.

> [!IMPORTANT]
> Este repositório **não distribui** o SafeSign Identity Client, suas bibliotecas, binários, instaladores ou qualquer outro componente proprietário. O usuário deve obter o instalador original por meios oficiais e observar os termos de licença do fornecedor.

## Compatibilidade

- Fedora 45 x86_64: compilação, instalação, reconhecimento do token G+D e configuração manual do Firefox validados na release 1.
- Release 2: configuração automática do Firefox implementada, aguardando validação em instalação real.
- Outras versões do Fedora e variantes atômicas: não validadas nesta versão.

## Finalidade

O SafeSign Identity Client é utilizado para gerenciamento de tokens criptográficos e smart cards usados com certificados digitais, incluindo certificados A3 em tokens USB.

Este projeto se limita a:

- fornecer metadados e scripts de empacotamento RPM;
- documentar o processo de build local;
- documentar a instalação no Fedora;
- registrar o módulo PKCS#11 do SafeSign no `p11-kit`;
- configurar automaticamente o Firefox RPM por meio da política `SecurityDevices.Add`;
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
sudo dnf install fedora-packager rpmdevtools rpm-build unzip tar gzip desktop-file-utils
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
cp safesign.module safesign-firefox-policy.py ~/rpmbuild/SOURCES/
```

Baixe o instalador oficial do SafeSign Identity Client na [página de downloads da G+D América do Sul](https://safesign.gdamericadosul.com.br/download). Selecione **Linux → Red Hat 10 (64 bits) → SafeSign 4.7.0.0**, obtenha o arquivo `SafeSign IC Standard Linux redhat10 4.7.0.0-AET.000.zip` e coloque-o em `~/rpmbuild/SOURCES/`. O download deve ser realizado diretamente pelo usuário, observando os termos de licença do fabricante.

Exemplo, ajustando o nome conforme o arquivo obtido:

```bash
cp "SafeSign IC Standard Linux redhat10 4.7.0.0-AET.000.zip" ~/rpmbuild/SOURCES/
```

O SPEC normaliza automaticamente o nome do ZIP com sublinhados na fase `%prep` e extrai `rpm_sources.tar.gz`.

### 4. Construir o pacote

```bash
cd ~/rpmbuild/SPECS/
rpmbuild -ba safesign-identity-client.spec
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
sudo dnf install ~/rpmbuild/RPMS/x86_64/safesign-identity-client-4.7.0.0-*.rpm
```

### Fedora Silverblue / Kinoite

Em sistemas atômicos, habilite o socket do PC/SC:

```bash
sudo systemctl enable --now pcscd.socket
```

Instale o RPM via `rpm-ostree`:

```bash
rpm-ostree install ~/rpmbuild/RPMS/x86_64/safesign-identity-client-4.7.0.0-*.rpm
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

A partir da release 2, o RPM executa o configurador em `%posttrans` e registra o módulo SafeSign para o Firefox nativo (RPM), inclusive quando o navegador ainda não está instalado.

O configurador integra a seguinte política ao arquivo `/etc/firefox/policies/policies.json`:

```json
{
  "policies": {
    "SecurityDevices": {
      "Add": {
        "SafeSign G+D": "/usr/lib64/libaetpkss.so"
      }
    }
  }
}
```

Outras políticas existentes são preservadas. Se o mesmo caminho já estiver registrado em `Add`, não é criado outro registro. Se o JSON estiver inválido, utilizar o formato legado de SecurityDevices, tiver um conflito de nome ou desabilitar explicitamente o módulo, o configurador informa o problema sem substituir o arquivo. Nesses casos, o administrador deve ajustar a política manualmente.

Para reaplicar a configuração:

```bash
sudo /usr/libexec/safesign-firefox-policy
```

Feche completamente o Firefox e abra-o novamente. Acesse `about:policies` e verifique a política ativa e a seção de erros. Em seguida, acesse `about:preferences#privacy` → **Certificados** → **Dispositivos de Segurança**.

Se o token já estiver disponível por p11-kit ou por registro manual, não adicione outra instância desnecessariamente.

### Configuração manual (alternativa)

1. Insira o token criptográfico.
2. Acesse `about:preferences#privacy`.
3. Em **Certificados**, clique em **Dispositivos de Segurança**.
4. Se o módulo ainda não estiver disponível, clique em **Carregar**.
5. Nome: `SafeSign G+D`; arquivo: `/usr/lib64/libaetpkss.so`.
6. Confirme e verifique o token e os certificados.

### Remoção e limitações

A política é configuração administrativa compartilhada e não é apagada automaticamente na desinstalação do RPM. Para removê-la, retire somente a entrada SafeSign de `SecurityDevices.Add` e, se necessário, descarregue o módulo em Dispositivos de Segurança. Não apague políticas de outros programas.

A configuração automática destina-se ao Firefox RPM. O Firefox Flatpak possui isolamento próprio e requer configuração específica; não foi validado. Em sistemas atômicos, confira a política após reiniciar e execute o configurador manualmente se necessário.

Referências: [SecurityDevices](https://firefox-admin-docs.mozilla.org/reference/policies/securitydevices/) e [Configuração de políticas](https://firefox-admin-docs.mozilla.org/guides/policies-configuration/).

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

Não publique o ZIP, o RPM binário gerado ou as bibliotecas proprietárias sem autorização do titular. A diretiva `NoSource: 0` exclui o ZIP do pacote-fonte, mas não autoriza redistribuição do RPM binário.

O **SafeSign Identity Client** e seus componentes binários são software proprietário de seus respectivos titulares, incluindo AET Europe B.V. e/ou G+D Mobile Security/G+D América do Sul, conforme o canal de distribuição utilizado. Este repositório não concede direitos sobre esses componentes proprietários.
