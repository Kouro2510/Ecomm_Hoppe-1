from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from .forms import LoginForm, MyPasswordResetForm, MyPasswordChangeForm, MySetPasswordForm
from .views import CreateCheckoutSessionView, ProductLandingPageView

urlpatterns = [
                  path("home", views.home, name="home"),
                  path("about", views.about, name="about"),
                  path("contact", views.contact, name="contact"),
                  path("category/<slug:val>", views.CategoryView.as_view(), name="category"),
                  path("product-detail/<int:pk>", views.ProductDetail.as_view(), name="product-detail"),
                  path("category-title/<val>", views.CategoryTitle.as_view(), name="category-title"),
                  path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
                  path('cart/', views.show_cart, name='showcart'),
                  path('checkout/', views.checkout.as_view(), name='checkout'),
                  path('paymentdone/', views.payment_done, name='paymentdone'),
                  path('orders/', views.home, name='orders'),
                  path('pluscart/', views.plus_cart),
                  path('minuscart/', views.minus_cart),
                  path('removecart/', views.remove_cart),
                  path('create-checkout-session', CreateCheckoutSessionView.as_view(), name = 'create-checkout-session'),
                  path('', ProductLandingPageView.as_view(), name = 'landing-page'),
                  # login authentication
                  path('registration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),
                  path('accounts/login.',
                       auth_view.LoginView.as_view(template_name='app/login.html', authentication_form=LoginForm),
                       name='login'),
                  path('password-reset/', auth_view.PasswordResetView.as_view(template_name='app/password_reset.html',
                                                                              form_class=MyPasswordResetForm),
                       name='password_reset'),
                  path('changepassword/', auth_view.PasswordChangeView.as_view(template_name='app/changepassword.html',
                                                                               form_class=MyPasswordChangeForm,
                                                                               success_url='/passwordchangedone'),
                       name='passwordchange'),
                  path('passwordchangedone/',
                       auth_view.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'),
                       name='passwordchangedone'),
                  path('profile/', views.ProfileView.as_view(), name='profile'),
                  path('address/', views.address, name='address'),
                  path('UpdateAddress/<int:pk>', views.UpdateAddress.as_view(), name='UpdateAddress'),
                  path('logout/', auth_view.LogoutView.as_view(next_page='login'), name='logout'),
                  path('password-reset/', auth_view.PasswordResetView.as_view(template_name='app/password_reset.html', form_class=MyPasswordResetForm),
                       name='password_reset'),
                  path('password-reset/done',
                       auth_view.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'),
                       name='password_reset_done'),
                  path('password-reset-complete/',
                       auth_view.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'),
                       name='password_reset_complete'),
                  path('password-reset-confirm/<uidb64>/<token>',
                       auth_view.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html',
                                                                  form_class=MySetPasswordForm),
                       name='password_reset_confirm'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
