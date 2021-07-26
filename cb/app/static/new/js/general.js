const MDCCheckbox = mdc.checkbox.MDCCheckbox;
const MDCChipSet= mdc.chips.MDCChipSet;
const MDCIconToggle = mdc.iconToggle.MDCIconToggle;
const MDCRipple = mdc.ripple.MDCRipple;
const MDCDialog = mdc.dialog.MDCDialog;
const MDCTabBar = mdc.tabs.MDCTabBar;
const MDCTextField = mdc.textField.MDCTextField;
const MDCSelect = mdc.select.MDCSelect;
const MDCSnackbar = mdc.snackbar.MDCSnackbar;
const MDCTabBarFoundation = mdc.tabs.MDCTabBarFoundation;


var CURRENT_NAME, loginAlert, logoutAlert, u_info, l_p, snackbar;
var alert_opt = [];
var s_al = 0;
var s_li = 0;
var s_lo = 0;
var dialog_evt = $.Event('rootdialogopened');
var auth_evt = $.Event('adminhere');
var out_evt = $.Event('logout');
var in_evt = $.Event('login');

$(document).ready(function() {
	window.mdc.autoInit();
	loginAlert = new MDCDialog(document.querySelector('.login-dialog'));
	logoutAlert = new MDCDialog(document.querySelector('.logout-dialog'));
	u_info = mdc.menu.MDCMenu.attachTo(document.querySelector('.mdc-menu'));
	
	// устанавливаем активную кнопку в навигационной панели
	var t = $("title").text().toLowerCase();
	var tabs = $("header .mdc-tab");
	switch (true) {
		case t.indexOf('главная')>=0:
			$(tabs[0]).addClass("mdc-tab--active");
			break
		case t.indexOf('поиск')>=0:
			$(tabs[1]).addClass("mdc-tab--active");
			break
		case t.indexOf('обновление')>=0:
			$(tabs[3]).addClass("mdc-tab--active");
			break
	}
	
	new MDCIconToggle(document.querySelector("#user-tab"));
	$("#user-tab").focus(function(){$(this).blur()});
	
	$('.exit').click(function(){
        $(window).trigger(dialog_evt);
        logoutAlert.show()
	});

	$(".login-field input").keydown(function(e) {
		if (e.which == 13) validateAuth()
	});
	
	// загрузочная панелька
	l_p = mdc.linearProgress.MDCLinearProgress.attachTo(document.querySelector("#progress"));
	load(1,true)
});

// вызываем два вида снэкбаров, если не нашли результатов или превысили порог
function callAlert(ind) {
	if (s_al == 0) snackbar = new MDCSnackbar(document.querySelector('.mdc-snackbar'));
	snackbar.show(alert_opt[ind])
}

// загрузочная панелька
function load(val,exit) {
	l_p.open();
	l_p.progress = val;
    if (exit) {
        setTimeout(function(){l_p.close()}, 1000);
        setTimeout(function(){l_p.progress = 0}, 2000);
    }
}

// показываем меню с информаицей о пользователе по клику на кнопку
function userMenu() {
	u_info.open = !u_info.open;
	if (s_lo == 0) {
		setTimeout(function(){
            new MDCRipple(document.querySelector('.user-settings'));
			new MDCRipple(document.querySelector('.exit'))
		},100)
	};
    s_lo++
}

// показываем диалоговое окно для входа в аккаунт
function showLogin() {
    $(window).trigger(dialog_evt);
	loginAlert.show();
	if (s_li == 0) {
		setTimeout(function(){
			var tf = $(".mdc-text-field");
			for (var i=0;i<tf.length;i++) {
				new MDCTextField(tf[i])
			}
		},100)
	};
    s_li++
}

// исправляем непорядок с CSRF
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

// не даём пользователю отправлять форму входа пустой и пробуем авторизовать
function validateAuth() {
	var form = $("#auth");
	var fields = $(".login-field input");
	var help_t = $(".must-fill");
	var invalid = false;
	for (var x=0;x < fields.length;x++) {
		if (fields[x].value == "") {
			$(fields[x]).parent('div').addClass("mdc-text-field--invalid");
			help_t.text('Поля должны быть заполнены');
			invalid = true
		}
	}
	if (!invalid) {
		help_t.animate({opacity: '0'},200);
		$.ajax({
			url: '/auth/',
			type: 'POST',
			data: {
				'username': $('#username').val(),
				'password': $('#password').val()
			},
			dataType: 'json',
			success: function (data) {
				if (data.l_in) {
					loginAlert.close();
					CURRENT_NAME = data.name;
					$('.us_inf-name span').text(data.nick);
					$('#user-tab').text('person').attr('onclick','userMenu()');
					if (data.admin) $(window).trigger(auth_evt);
					$('input[name="csrfmiddlewaretoken"]').val(getCookie('csrftoken'));
					load(1,true);
					setTimeout(function(){
						form.trigger('reset');
						$(window).trigger(in_evt);
					},250)
				} else {
					help_t.text('Неверный логин/пароль');
					help_t.animate({opacity: '1'},200)
				}
			}
		});
	} else {
		help_t.animate({opacity: '1'},200)
	}
}

// выходим из системы
function authLogout() {
	load(0.9,false);
	$.ajax({
		url: '/auth/',
		type: 'POST',
		dataType: 'json',
		success: function (data) {
			if (data.l_out) {
				$('.us_inf-name span').text('username');
				$('#user-tab').text('person_outline').attr('onclick','showLogin()');
				$(window).trigger(out_evt);
				$('input[name="csrfmiddlewaretoken"]').val(getCookie('csrftoken'));
				load(1,true)
			}
		}
	});
}

// показываем уведомление об успешном входе в систему
function loginSuccess() {
    $(".login-alert").addClass('success');
    setTimeout(function(){$(".login-alert").removeClass('success')},3000)
}

// проверяем, авторизован ли юзер
function checkAuth(){
	var result = false;
	$.ajax({
		url: '/auth/',
		dataType: 'json',
		async: false,
		success: function (data) {
			if (data.auth_good) result = true
		}
	})
	return result
}

// проверяем на наличие файла обновления
function checkUpdate() {
	var result = false;
	$.ajax({
		url: '/sys_block/',
		dataType: 'json',
		async: false,
		success: function (data) {
			if (data.has_excel) result = true
		}
	});
	return result
}

// получаем какой-нибудь куки
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break
            }
        }
    }
    return cookieValue;
}
