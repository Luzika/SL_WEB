"""
URL configuration for testproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import include, path
from User.views import defaultView, loginView, loggedIn, loggedOut, adminView
from User.views import omegaManageView, omegaMonitorView, omegaDownloaded
from Shipment.views import mainView1, mainDownloaded1, mainUpdated1, pageSelect, stickShipment_ajax
from Shipment.views import mainView2, mainDownloaded2
from Shipment.views import mainShipmentSuccessM
from Shipment import views

### Must have these lines to include url to the static files (images/files)
from django.conf import settings
from django.conf.urls.static import static

### for API ####
from rest_framework.routers import DefaultRouter
from Shipment.api.views import ExternalShipmentAPI
router = DefaultRouter()
router.register(r'ext', ExternalShipmentAPI, basename='ext')

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('main1/get_shipment_details_ajax/', views.get_shipment_details_ajax, name='get_shipment_details_ajax'),
    path('tracking/<str:shipment_id>/', views.shipmentTrackingView, name='shipmentTrackingView'),
    path('tracking/<str:shipment_id>/update/', views.updateShipment, name='updateShipment'),
    path('customer-tracking/', views.customerTracking, name='customerTracking'),
    path('submit-evaluation/', views.submit_evaluation, name='submit_evaluation'),
    path('', defaultView, name="default"),
    path('', loggedOut, name="logoutPage"),
    path('login/', loginView, name="loginPage"),
    path('admini/', adminView, name="adminPage"),
    path('main1/', mainView1, name="mainPage1"),
    path('main2/', mainView2, name="mainPage2"),
    path('approve_pending_shipment/<int:pk>/', views.approve_pending_shipment, name='approve_pending_shipment'),
    path('reject_pending_shipment/<int:pk>/', views.reject_pending_shipment, name='reject_pending_shipment'),
    path('main1/mobile/', mainView1, name='mainPageMobile1'),
    path('Supdated1/', mainUpdated1, name="mainUpdated1"),
    path('Sdownloaded1/', mainDownloaded1, name="mainDownloaded1"),
    path('Sdownloaded2/', mainDownloaded2, name="mainDownloaded2"),
    path('main1/pageSelect', pageSelect, name='pageSelect'),
    path('shipment/success/mobile/', mainShipmentSuccessM, name='shipmentAddedSuccessM'),
    # NEW DEDICATED PATH for AJAX tickbox updates
    path('main1/stick_ajax/', stickShipment_ajax, name='stickShipment_ajax'),
    path('loginConfirmed/<str:loggedID>#<str:roleLogin>#', loggedIn,
         name="loginConfirmed"),
    path('OMeGaDMin/Umanage/', omegaManageView,
         name="omegaManagePage"),
    path('OMeGaDMin/Umonitor/', omegaMonitorView,
         name='omegaMonitorPage'),
    path('OMeGaDMin/Udownloaded/', omegaDownloaded,
         name="omegaDownloaded"),
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
