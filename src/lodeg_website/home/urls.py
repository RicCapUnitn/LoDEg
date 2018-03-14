from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^contact/', views.contact, name='contact'),
    url(r'^user/', views.user, name='user'),
    url(r'^courseInfo/', views.courseInfo, name='courseInfo'),
    url(r'^userInfo/', views.userInfo, name='userInfo'),
    url(r'^sessionInfo/', views.sessionInfo, name='sessionInfo'),
    url(r'^collectDataFromDb/', views.collectDataFromDb, name='collectDataFromDb'),
    url(r'^saveDataToDb/', views.saveDataToDb, name='saveDataToDb'),
    url(r'^exportToCsv/', views.exportToCsv, name='exportToCsv'),
    url(r'^setUser/', views.setUser, name='setUser'),
    url(r'^setSession/', views.setSession, name='setSession'),
    url(r'^setLesson/', views.setLesson, name='setLesson'),
    url(r'^setCourse/', views.setCourse, name='setCourse'),
    url(r'^sendEmail/', views.sendEmail, name='sendEmail'),
    url(r'^executeCompleteExtraction/', views.executeCompleteExtraction,
        name='executeCompleteExtraction'),
    url(r'^$', views.index, name='index'),

    url(r'^settings/', views.settings, name='settings'),
    url(r'^modifySystemSettings/', views.modifySystemSettings,
        name='modifySystemSettings'),
    url(r'^debuggingConsole/', views.debuggingConsole, name='debuggingConsole')
]
