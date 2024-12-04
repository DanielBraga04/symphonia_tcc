from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from biblioteca.models import Partitura

User = get_user_model()

def home(request):
    return render(request, 'index.html')

def sobrenos(request):
    return render(request, 'sobre_nos.html')

def cadastro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')

        # Verifica se o e-mail já existe
        if User.objects.filter(email=email).exists():
            messages.error(request, 'E-mail já está em uso.')
            return redirect('cadastro')

        # Cria o usuário com os campos adicionais
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('login')

    return render(request, 'cadastro.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            request.session['user_data'] = {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'password': user.password
            }
            return redirect('perfil')
        else:
            if not email or not User.objects.filter(email=email).exists():
                messages.error(request, "Email ou Username incorreto!")
            elif not user:
                messages.error(request, "Senha incorreta!")
            else:
                messages.error(request, "Email e senha incorretos!")
    
    return render(request, 'login.html')

def user_profile_view(request):
    user = request.user
    errors = {}
    success_message_general = None
    success_message_password = None
    active_section = 'general'  # Aba padrão é "Geral"

    if request.method == 'POST':
        # Verificar se é uma solicitação para mudar senha ou atualizar dados gerais
        if 'current-password' in request.POST:  # Alteração de Senha
            active_section = 'password'
            current_password = request.POST.get('current-password')
            new_password = request.POST.get('new-password')
            confirm_password = request.POST.get('confirm-password')

            # Validar a senha
            if not user.check_password(current_password):
                errors['current_password'] = 'Senha atual está incorreta.'
            elif new_password != confirm_password:
                errors['confirm_password'] = 'As senhas não coincidem.'
            elif len(new_password) < 8:
                errors['new_password'] = 'A senha nova deve ter pelo menos 8 caracteres.'
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                success_message_password = 'Senha alterada com sucesso.'
        else:  # Atualizar dados gerais
            active_section = 'general'
            # Validar e atualizar os dados do usuário
            user.username = request.POST.get('username')
            user.first_name = request.POST.get('first-name')
            user.last_name = request.POST.get('last-name')
            user.email = request.POST.get('email')
            user.phone = request.POST.get('phone')
            user.save()
            success_message_general = 'Informações atualizadas com sucesso.'
            

    partituras = user.partituras.all()

    # Renderiza a página com a aba ativa definida
    return render(request, 'user_profile.html', {
        'user_data': user,
        'errors': errors,
        'success_message_general': success_message_general,
        'success_message_password': success_message_password,
        'active_section': active_section,
        'partituras': partituras,
    })

def logout_view(request):
    logout(request)
    return redirect('login')

def excluir_partitura_logado(request, partitura_id):
    partitura = get_object_or_404(Partitura, pk=partitura_id)
    if request.method == 'POST':
        partitura.delete()
        return redirect('perfil')  # Redireciona para a página principal após excluir
    return render(request, 'excluir_partitura.html', {'partitura': partitura})

def home_logado(request):
    return render(request, 'index_logado.html')

def sobre_nos_logado(request):
    return render(request, 'sobre_nos_logado.html')

