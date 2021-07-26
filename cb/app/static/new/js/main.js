const one = 'mdc-toolbar--flexible-space-minimized';
const two = 'mdc-toolbar--flexible-space-maximized';

var hist = $('.history');
var h_tb = $('.hist-top');
var h_cl = document.querySelector('#hist-close');
var ovf = $('.ovf-shade');
var showed = false;
var activate = false;
var has_scroll = false;
var records, init_w, init_h, scroll, fade_time, h_cl_obj, action_chips;
var selects = [];
var h_rows = [];

$(window).on('rootdialogopened', function () {
    if (hist.hasClass('full')) closeHistory()
}).on('adminhere', function () {
	hist.toggleClass('no-actions').addClass('showing-actions')
}).on('login', function () {
	$('.login-alert p:first-child').append(CURRENT_NAME);
	loginSuccess()
}).on('logout', function () {
	var l_a = $('.login-alert p:first-child');
	var str = l_a.text();
	l_a.text(str.replace(str.split(" ")[2],''))
});

$(document).ready(function() {
	// зажигаем часики
	startTime();
	// устанавливаем картиночку на фон
	var time_points = setPicture(false,0);

	// показываем виджет целиком
	$('.hist-action').click(showHistory);
});

function showHistory() {
    console.log('Opening history widget!');
    
    if (!showed) {
        init_h = hist.height();
        init_w = hist.width();
        hist.css({'height': init_h, 'width': init_w})
    }
    
	hist.children('div:last-child').fadeOut( 100 );
    
	setTimeout(function(){
		$('.hist-back').toggleClass('dark');
		hist.css({'height': '80%', 'width': '600px'}).toggleClass('full');
        scrollHandler(false)
	}, 150);
    
	setTimeout(function(){
        historyHandler(true);
        h_tb.fadeIn( fade_time );
		hist.toggleClass('up-fade down-fade fade');
		
        $(h_cl).click(closeHistory);
        h_cl_obj = new MDCIconToggle(h_cl);
        if (!showed) {
			action_chips = new MDCChipSet(document.querySelector('.mdc-chip-set'));
			$('.select-all').click(function() {
				var init_state = action_chips.chips[1].isSelected()
				action_chips.chips[1].foundation.setSelected(!init_state);
				$.each(selects, function(x, el) {el.checked = !init_state})
			});
			$('.delete').click(function() {
				var del = 0;
				for (z=0;z<selects.length;z++) {
					if (selects[z-del].checked == true) {
						selects.splice(z-del,1);
						h_rows.splice(z-del,1);
						$(records[z-del]).slideUp();
						records.splice(z-del,1);
						del++
					}
				}
				scrollHandler(false)
			});
			showed = true
		}
	}, 700);
}
function closeHistory() {
    console.log('Closing history widget!');
    
    h_cl_obj.destroy();
    $(h_cl).off('click');
	historyHandler(false);
    h_tb.fadeOut( fade_time+350 );
	hist.toggleClass('up-fade down-fade fade');
    
    setTimeout(function(){
        hist.css({'height': init_h, 'width': init_w}).toggleClass('collapsing full');
        $('.hist-back').toggleClass('dark');
        scrollHandler(true)
    }, fade_time+250);
    
    setTimeout(function(){
        toolbarHandler(true);
        hist.toggleClass('collapsing');
        hist.children('div:last-child').fadeIn( 100 )
    }, fade_time+650);
    h_rows = []
}
function historyHandler(down) {
    fade_time = 0;
    records = $('.hist-list li');
    var record_h = records.first().height();
    if (!hist.hasClass('no-actions')) activate = true
    else activate = false;
    if (down) var arr = records
    else var arr = records.get().reverse();
    
    $.each(arr, function(val, li) {
        if (down) {
            if (!showed) {
                var obj = new MDCCheckbox(li.querySelector('.hist-check'));
                selects.push(obj)
            }
            var obj1 = new MDCRipple(li);
            h_rows.push(obj1);
            actionHandler(li, val)
        } else {
            val = (records.length-1)-val;
            h_rows[val].destroy();
            $(li).off('click');
        }
        if ((val+1)*record_h <= $('.hist-inner').height()+80) {
            $(li).css('transitionDelay', fade_time+'ms');
            fade_time += 50
        } else $(li).css('transitionDelay', '');
    });
    fade_time -= 50
}
function scrollHandler(force) {
    var need_scroll = $('.hist-list').height() > $('.hist-inner').height();
    if (has_scroll && force || has_scroll && !need_scroll) scrollDestroy()
    else if (!has_scroll && need_scroll) {
        scrollBuild();
        ovf.addClass('active')
    }
}
function scrollBuild() {
    has_scroll = true;
    hist.toggleClass('with-scroll');
    ovf.fadeIn();
    scroll = new SimpleBar(document.getElementById('scroll'), { autoHide: false });
    scroll.getScrollElement().addEventListener('scroll', function() {
        if ($(this).scrollTop() == 0) toolbarHandler(true)
        else toolbarHandler(false);
        if ($(this).scrollTop()+this.offsetHeight >= scroll.getContentElement().offsetHeight)
            ovf.removeClass('active')
        else ovf.addClass('active')
    })
}
function scrollDestroy() {
    has_scroll = false;
    ovf.fadeOut();
    scroll.unMount();
    $('.simplebar-content').children().appendTo('#scroll');
    $('[class*="simplebar"]').each(function() {$(this).remove()});
    hist.toggleClass('with-scroll');
    $('#scroll').removeAttr('data-simplebar')
}
function toolbarHandler(check) {
    if (check) h_tb.removeClass(one).addClass(two)
    else h_tb.removeClass(two).addClass(one)
}
function actionHandler(el, ind) {
    if (activate) {
    	selects[ind].disabled = false;
        $(el).click(function(e) {
            if (e.target === this) {
				if (action_chips.chips[1].isSelected())	action_chips.chips[1].foundation.setSelected(false);
				selects[ind].checked = !selects[ind].checked
			}
        })
    } else {
    	selects[ind].checked = false;
    	selects[ind].disabled = true
	}
}
function getHistory() {
	$.ajax({
		url: '/index/',
		data: {
			'init_number': records.length
		},
		dataType: 'html',
		success: function (data) {
			$('.hist-list').append(data)
		}
	});
}

function setPicture(demo,demo_value) {
	var now = new Date();
	var times = seasonTime(now);
	now = now.getTime();
	
	// для начала проверяем на исключения, когда начало/конец того, что
	// мы считаем "днём" не совпадает с началом процессов рассвета/заката
	if (times[8]<times[0]) var late_sunr = true;
	if (times[7]<times[9]) var early_suns = true;
	
	// теперь прописываем все возможные сценарии
	switch (true) {
		case (now<times[0]&&(!(late_sunr) || now<times[8])
			  || now>=times[7]&&(!(early_suns) || now>=times[9])):
			$("body").css("background-image", "url('/static/new/img/night.jpg')");
			break
		case (now<times[1]&&(now>=times[0] || now>=times[8]&&late_sunr)
			  || now>=times[6]&&(now<times[7] || now<times[9]&&early_suns)):
			$("body").css("background-image", "url('/static/new/img/night2.jpg')");
			break
		case (now<times[2]&&now>=times[1]):
			$("body").css("background-image", "url('/static/new/img/twilight1.jpg')");
			break
		case (now<times[3]&&now>=times[2]):
			$("body").css("background-image", "url('/static/new/img/sunrise.jpg')");
			break
		case (now<times[4]&&now>=times[3]):
			$("body").css("background-image", "url('/static/new/img/day.jpg')");
			break
		case (now<times[5]&&now>=times[4]):
			$("body").css("background-image", "url('/static/new/img/sunset.jpg')");
			break
		case (now<times[6]&&now>=times[5]):
			$("body").css("background-image", "url('/static/new/img/twilight2.jpg')");
			break
	}
	
	// отдельно - для надписи, так как там есть небольшие отличия
	switch (true) {
		case (now<times[8] || now>=times[9]):
			$(".welcome").html("Доброй ночи!");
			break
		case (now>=times[8]&&now<times[10]):
			$(".welcome").html("Доброе утро!");
			break
		case (now>=times[10]&&now<times[11]):
			$(".welcome").html("Добрый день!");
			break
		case (now>=times[11]&&now<times[9]):
			$(".welcome").html("Добрый вечер!");
			break
	}
	
	setTimeout(function(){setPicture()},900000);
	return(times)
}

function startTime() {
    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    var s = today.getSeconds();
    m = checkTime(m);
    s = checkTime(s);
	$("#clock").html(h+':'+m+':'+s);
	if (h < 10) $("#clock").css("margin-right","-30px");
	if (h > 9 & h<20) $("#clock").css("margin-right","-10px");
    var t = setTimeout(startTime, 500);
}
function checkTime(i) {
    if (i < 10) {i = "0" + i};  // добавить ноль перед числами < 10
    return i;
}

// лого меняется, если навигационная панель слишком узкая
function resizing() {
	var w = window.innerWidth;
	if (w<1000) {
		$(".logo").html("<img src='/static/new/img/CB-logo-min.png'>");
	} else {
		$(".logo").html("<img src='/static/new/img/CB-logo.png'>");
	}
}

// дополнительная функция для удобного округления
function precisionRound(number, precision) {
  var factor = Math.pow(10, precision);
  return Math.round(number * factor) / factor;
}

// тут долго и нудно находим нужные контрольные
// временные точки для отображения фона
function seasonTime(now) {
	// этот кусок кода позволяет вычислить, какой
	// сегодня по счёту день в году
	var start = new Date(now.getFullYear(), 0, 0);
	var diff = (now - start) + ((start.getTimezoneOffset() - now.getTimezoneOffset()) * 60 * 1000);
	var oneDay = 1000 * 60 * 60 * 24;
	var day = Math.floor(diff / oneDay);
	
	// далее - коэффициенты для функций вычисления времени
	// восхода/заката, получены через Excel
	const sunr_par1 = [0.00000184763949328257,
					 -0.000459377203073874,
					 -0.00647695197872622,
					 9.03347216036568];
	const sunr_par2 = [-0.000000000118550432046054,
					 0.0000000563258816456847,
					 -0.0000101635843282044,
					 0.000881315775444591,
					 -0.00481943454667544,
					 3.77338232491456];
	const suns_par1 = [-0.00000000378951205766594,
					 0.000000732687323853898,
					 -0.000028296409412043,
					 0.0335632446096383,
					 16.0124308318809];
	const suns_par2 = [0.00000189380220801181,
					 -0.000495105027354448,
					 -0.00207881725347647,
					 21.3410361959413];
					 
	// здесь обозначаем дельты времени для начала
	// показа того или иного сценария фона
	var add_sunr = [-120,-60,0,90];
	var add_suns = [-90,0,60,120];
	
	// чтобы было дальше удобно создавать контрольную
	// точку - сегодняшняя дата готовится заранее
	var str_default = now.getFullYear()+" "+(now.getMonth()+1)+" "+now.getDate()+" ";
	
	// в этом массиве будут собраны, собственно, сами контрольные точки
	var result = [];
	result.length = 12;
	
	// поскольку области определения функций пересекаются,
	// прописываем как их комбинировать
	switch (true) {
        case (day<170):
			var pars = [sunr_par1,suns_par1];
			break;
        case (day>169 && day<178):
			var pars = [sunr_par2,suns_par1];
			break;
        case (day>177):
			var pars = [sunr_par2,suns_par2];
			break;
    }
	
	// рабочая лошадка, забирает каждую контрольную
	// точку из функции-обработчика
	for (var j=0;j<pars.length;j++) {
		for (var z=0;z<4;z++) {
			if (j==1) add_sunr = add_suns;
			result[4*j+z] = getSunTime(str_default,day,pars[j],add_sunr[z])
		}
	}
	
	// ах да, у нас же есть ещё точки, которые задают промежуток
	// того, что мы считаем "днём", добавим их ручками
	result[8] = (new Date(str_default+"5:00")).getTime();
	result[9] = (new Date(str_default+"23:00")).getTime();
	result[10] = (new Date(str_default+"10:00")).getTime();
	result[11] = (new Date(str_default+"17:00")).getTime();
	
	return(result)
}
function getSunTime(str_default,day,coefs,add) {
	var k = 0;
	
	// используя принятый набор коэффициентов,
	// находим таки нужное время для данного дня
	for (var i=0;i<coefs.length;i++) {
		k+=coefs[i]*Math.pow(day, coefs.length-i-1);
	}
	
	// на предыдущем шаге получили число с дробной частью -
	// избавляемся от неё и собираем контрольную точку
	k*=60;
	
	var str = Math.floor((k+add)/60)+":"+precisionRound((k+add)%60,0);
	var out = (new Date(str_default+str)).getTime();
	// alert(out);
	return(out)
}