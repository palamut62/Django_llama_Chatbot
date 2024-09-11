from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import Chat, Message
import ollama
from groq import Groq
import os
from django.views.decorators.http import require_POST
import re
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt

client = Groq(api_key="key")

def get_models():
    return [model['name'] for model in ollama.list()['models']]

def generate_summary(message):
    summary_prompt = f"Summarize this message in 5 words or less: {message}"
    summary_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text briefly."},
            {"role": "user", "content": summary_prompt}
        ]
    )
    return summary_response.choices[0].message.content.strip()

def process_message_content(content):
    def replace_code_block(match):
        language = match.group(1) or 'plaintext'
        code = escape(match.group(2))
        return f'<pre><code class="language-{language}">{code}</code></pre>'

    # Kod bloklarını işle
    content = re.sub(r'```(\w+)?\n(.*?)```', replace_code_block, content, flags=re.DOTALL)
    
    # Satır içi kodları işle
    content = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', content)
    
    return content

@csrf_exempt
@require_POST
def chat_view(request):
    try:
        if request.POST.get('new_chat'):
            new_chat = Chat.objects.create(summary="Yeni Sohbet")
            return JsonResponse({
                'success': True, 
                'chat_id': new_chat.id,
                'summary': new_chat.summary
            })
        
        user_message = request.POST.get('message')
        chat_id = request.POST.get('chat_id')
        
        if not chat_id:
            return JsonResponse({'success': False, 'error': 'Chat ID is required'})

        chat = Chat.objects.get(id=chat_id)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": user_message}]
        )
        ai_response = response.choices[0].message.content

        Message.objects.create(chat=chat, content=user_message, is_user=True)
        Message.objects.create(chat=chat, content=ai_response, is_user=False)

        if chat.messages.count() == 2:
            summary = generate_summary(user_message)
            chat.summary = summary
            chat.save()

        return JsonResponse({
            'success': True, 
            'message': process_message_content(ai_response),
            'chat_id': chat.id, 
            'summary': chat.summary
        })
    except Exception as e:
        import traceback
        print("Hata:", str(e))
        print("Traceback:", traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})

def chat_page(request, chat_id=None):
    chats = Chat.objects.all().order_by('-timestamp')
    
    if not chat_id:
        chat_id = request.GET.get('chat_id')
    
    if not chat_id and chats.exists():
        return redirect('chat_page', chat_id=chats.first().id)
    
    try:
        current_chat = Chat.objects.get(id=chat_id) if chat_id else None
        messages = current_chat.messages.all().order_by('timestamp') if current_chat else []
        messages = [
            {
                'content': process_message_content(msg.content),
                'is_user': msg.is_user
            } for msg in messages
        ]
    except Chat.DoesNotExist:
        current_chat = None
        messages = []

    models = get_models()
    return render(request, 'chat/chat.html', {
        'chats': chats,
        'messages': messages,
        'models': models,
        'current_chat_id': current_chat.id if current_chat else None
    })
     

@require_POST
def delete_chat(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
        chat.delete()
        
        return JsonResponse({'success': True})
    except Chat.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sohbet bulunamadı.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def load_chat(request):
    chat_id = request.GET.get('chat_id')
    if chat_id:
        messages = Message.objects.filter(chat__chat_id=chat_id).order_by('timestamp')
        messages = [
            {
                'content': process_message_content(msg.content),
                'is_user': msg.is_user
            } for msg in messages
        ]
        return render(request, 'chat/messages.html', {'messages': messages})
    return HttpResponse('')

def index(request):
    return render(request, 'chat/index.html')
