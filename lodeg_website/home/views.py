from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.core.mail import EmailMessage


from django.contrib.auth.decorators import login_required

from .pythonML.system import LodegSystem

context = {
    "system": LodegSystem(),
    "adminPermissions": False,
    "contact_mail_address" : "capraroriccardo@gmail.com"
}

# Useful decorators
def set_context_user(func):
    def func_wrapper(request):
        context['user'] = request.user.lodeguser.lodeg_user_id 
        return func(request)
    return func_wrapper

def check_permissions(func): 
    def func_wrapper(request):
        if request.user.is_superuser:
            context['adminPermissions'] = True
        else:
            context['adminPermissions'] = False        
        return func(request)
    return func_wrapper

def course_required(func):
    def func_wrapper(request):
        if 'course' in context:
            return func(request)
        else:
            return  HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return func_wrapper

@login_required
@set_context_user
@check_permissions
def index(request):
    template_name = "base_admin.html" if context['adminPermissions'] else "base_user.html"
    context['template_name'] = template_name
    return render(request, 'home/index.html', context)

@login_required
def contact(request):
    return render(request, 'home/contact.html')

@login_required
@set_context_user
def courseInfo(request):
    return render(request, 'home/courseInfo.html', context)

@login_required
def userInfo(request):
    return render(request, 'home/userInfo.html', context)

@login_required
def sessionInfo(request):
    return render(request, 'home/sessionInfo.html', context)    

@login_required
@set_context_user
def user(request):
    return render(request, 'home/user.html', context)


@login_required
@check_permissions
def collectDataFromDb(request):
    if(context['adminPermissions'] == True):
        context['system'].collectDataFromDb()
    else:
        context['system'].collectDataFromDb(context['user'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@check_permissions
def saveDataToDb(request):
    if(context['adminPermissions'] == True):
        context['system'].saveDataToDb()
    else:
        context['system'].saveDataToDb(context['user'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@check_permissions
@course_required
def exportToCsv(request):   
    # Need to add something here to prompt the user for course if not selected
    return context['system'].getCSV(context['course'])

@login_required
def extractUserData(request):
    context['system'].extractUserData(context['user'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def executeCompleteExtraction(request):
    context['system'].executeCompleteExtraction()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_http_methods(["POST"])
def setUser(request):
    context['user'] = str(request.POST.get('selected_user'))
    if 'session' in context:
        del context['session']
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_http_methods(["POST"])
def setSession(request):
    context['session'] = str(request.POST.get('selected_session'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_http_methods(["POST"])
def setLesson(request):
    context['lesson'] = str(request.POST.get('selected_lesson'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_http_methods(["POST"])
def setCourse(request):
    context['course'] = str(request.POST.get('selected_course'))
    if 'user' in context:
        del context['user']
    if 'session' in context:
        del context['session']
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_http_methods(["POST"])
def sendEmail(request):  
    message = EmailMessage(
        'LoDEg bug report by: ' + request.POST.get('name'),
        request.POST.get('comment'),
        request.POST.get('mail') if request.POST.get('mail') is not None else 'not_specified@example.com',
        [context['contact_mail_address']]
    )
    
    attachment = request.POST.get('attachment')
    if attachment is not None:
        try:
            message.attach_file(attachment)
        except:
            pass
        
    message.send(fail_silently=False)
    
    #return render(request, 'home/index.html')

@login_required
@check_permissions
def debuggingConsole(request):
    import pdb; pdb.set_trace()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))