# SafeSign Identity Client para Fedora

Este repositório contém o arquivo de especificação (`.spec`) para gerar de forma automatizada o pacote RPM do **SafeSign Identity Client (Versão 4.6.0.0)** para o ecossistema Fedora. O projeto foi desenhado para portar o binário homologado para Red Hat Enterprise Linux 10, garantindo compatibilidade com o Fedora Workstation e variantes atômicas baseadas em `rpm-ostree` (como Fedora Silverblue e Kinoite).

Este cliente é utilizado para o gerenciamento de tokens criptográficos e smart cards emissores de certificados digitais (como os da **AC Defesa / Ministério da Defesa** e **G+D América do Sul**).

---

## 🚀 Como Construir o Pacote (Build Local)

Por se tratar de um software proprietário, você precisará baixar o arquivo-binário original e gerar o instalador na sua própria máquina para uso pessoal.

### 1. Instalar as Ferramentas de Construção
Certifique-se de que seu sistema possui as dependências necessárias para compilação de pacotes RPM:
```bash
sudo dnf install fedora-packager rpkg rpm-build unzip cpio

2. Preparar a Árvore do RPM Development
Bash

rpmdev-setuptree

3. Obter os Arquivos

    Baixe o arquivo safesign-identity-client.spec deste repositório e coloque-o em ~/rpmbuild/SPECS/.

    Baixe o arquivo binário oficial compactado (SafeSign_IC_Standard_Linux_redhat10_4.6.0.0-AET.000.zip) do portal oficial da G+D América do Sul e mova-o para a pasta de fontes do RPM:

Bash

mv "SafeSign IC Standard Linux redhat10 4.6.0.0-AET.000.zip" ~/rpmbuild/SOURCES/

4. Executar a Compilação
Bash

cd ~/rpmbuild/SPECS/
rpmbuild -bb safesign-identity-client.spec

O pacote gerado (.rpm) estará disponível na pasta ~/rpmbuild/RPMS/x86_64/.
📦 Instalação do Pacote no Sistema
No Fedora Workstation (Padrão)
Bash

sudo dnf install pcsc-lite pcsc-lite-libs
sudo systemctl enable --now pcscd
sudo dnf install ~/rpmbuild/RPMS/x86_64/safesign-identity-client-4.6.0.0-*.rpm

No Fedora Atômico (Silverblue / Kinoite)
Bash

sudo systemctl enable --now pcscd
rpm-ostree install ~/rpmbuild/RPMS/x86_64/safesign-identity-client-4.6.0.0-*.rpm

Nota: Após a instalação via rpm-ostree, é necessário reiniciar o sistema.
🦊 Instalação e Configuração no Mozilla Firefox

Para que o Firefox consiga utilizar o seu certificado digital A3 (Token USB), a biblioteca PKCS#11 do SafeSign precisa ser instalada/registrada no navegador. Isto pode ser feito de duas formas: Automatizada (via políticas) ou Manual (via interface do Firefox).
Método 1: Instalação Automatizada (Recomendado)

Para instalar o módulo de forma permanente em todos os perfis do Firefox do sistema, você pode criar um arquivo de políticas. Isto fará com que o Firefox carregue o driver do token automaticamente sem que você precise configurar nada manualmente após abrir o navegador.

Execute o seguinte comando no terminal para criar a política de segurança:
Bash

sudo mkdir -p /etc/firefox/policies
sudo tee /etc/firefox/policies/policies.json <<EOF
{
  "policies": {
    "SecurityDevices": {
      "SafeSign PKCS11": "/usr/lib64/libaetpkss.so"
    }
  }
}
EOF

Nota para Silverblue/Kinoite: O caminho /etc é mutável (leitura e escrita), pelo que este método funciona perfeitamente em sistemas atômicos.
Método 2: Instalação e Ativação Manual (Interface Gráfica)

Se preferir instalar o driver apenas no seu perfil de usuário atual através da interface do navegador, siga as diretrizes adaptadas do manual da AC Defesa:
Para Certificados A3 (Token USB / Hardware)

    Insira o seu Token criptográfico numa porta USB da máquina.

    Abra o Mozilla Firefox e aceda à URL de configurações de privacidade digitando na barra de endereços:
    about:preferences#privacy

    Role a página até ao fim e, dentro da seção Certificados, clique em Dispositivos de Segurança....

    Na janela do Gerenciador de Dispositivos, clique no botão Carregar localizado no menu à direita.

    Preencha os campos da janela flutuante da seguinte forma:

        Nome do módulo: SafeSign PKCS#11 Module

        Nome do arquivo do módulo: Clique em Procurar... e aponte para o caminho da biblioteca instalada pelo pacote:
        /usr/lib64/libaetpkss.so

    Clique em Abrir, confirme em OK e certifique-se de que o dispositivo foi listado corretamente na árvore lateral esquerda. Ele passará a exibir o estado "Ativo" ou "Pronto" assim que ler o token USB.

Para Certificados A1 (Formato de Software .pfx / .p12)

    Aceda a about:preferences#privacy no Firefox.

    Role até ao rodapé da página e selecione Ver Certificados....

    Na aba Seus certificados, clique em Importar....

    Navegue até ao local onde está armazenado o seu arquivo .pfx ou .p12, selecione-o e clique em Abrir.

    Insira o PIN/Senha de proteção que foi gerado no backup do certificado para concluir a validação.

🛠️ Solução de Problemas (Troubleshooting)

Se o token não responder ou o Firefox indicar que o dispositivo está inacessível, valide se o serviço do barramento do smart card está ativo no seu terminal Fedora:
Bash

# Verifique se o daemon do pcscd está rodando perfeitamente
systemctl status pcscd

# Monitore em tempo real a inserção e comunicação do hardware
pcsc_scan

⚖️ Licença e Direitos Autorais

O arquivo .spec e as instruções de portabilidade contidas neste repositório são distribuídos sob a licença open-source MIT. O software binário final extraído e empacotado (tokenadmin, libaetpkss.so) é de propriedade exclusiva e autoral da AET Europe B.V. / G+D Mobile Security, distribuído sob termos proprietários pela G+D América do Sul.
