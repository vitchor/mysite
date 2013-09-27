Tutorial de Setup do Workspace Dyfocus:

1. Instalar git:
Instalar e configurar nome e email
(primeira parte de https://help.github.com/articles/set-up-git)
Criar e adicionar chave ssh ao github (https://help.github.com/articles/generating-ssh-keys)

2. Instalar mysql (http://www.macminivault.com/mysql-mountain-lion/)
*Se nao achar o egg : sudo ln -s /usr/local/mysql/lib/libmysqlclient.18.dylib /usr/lib/libmysqlclient.18.dylib

3. Restore mysql db:
Baixar o programa mysql administrator.
criar db chamado "pool" no mysql (sudo mysql; create database pool;)
Utilizando o administrator dar um "Restore" no db pool com o arquivo mais novo da pasta do dropbox: Dynafocus > Backups Mysql.

4. Instalar Xcode com ferramentas de terminal:
Baixar e instalar do developer.apple
Entrar em XCode > Preferences> Download e baixar "Terminal Tools"

5. Instalar modulos python (pode tbm usar sudo easy_install pip, e fazer tudo pelo pip):
  - sudo easy_install django
  - sudo easy_install boto
  - sudo easy_install mysql-python
  - sudo easy_install PIL

6. Baixar os dois projetos do github:
git clone https://github.com/vitchor/mysite.git
git clone https://github.com/vitchor/DynaFocus.git

7. Configurar o arquivo mysite > mysite > settings.py (usuario/senha do db e os caminhos para o projeto onde estiverem os valores "../ubuntu/..")

8. Rodar o servidor:
Ir para a pasta mysite
python manage.py runserver 8000

9. Adicionar Certificado/Chaves/ProvisioningProfiles da Apple	:
Arraste o arquivo do dropbox Dynafocus > Cert > Certificates2.p12 para o icone de sua keychain assistante.
Arraste o arquivo do dropbox Dynafocus > Cert > nuouuw.mobileprovision para o icone do seu xcode. 



Pronto! O servidor deve estar rodando e o projeto de iPhone tbm esta pronto pra ser editado.
Qualquer duvida ou mudanca adicionem dicas e comentarios ao tutorial.
Obrigado! 
