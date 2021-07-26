const has_topnav = false;

var card_nav, card_nav1, slides, lastTabInd, check_huy;
var select_menus = [];
var chipsets = [];
var checkboxes = [];
var fields_memo = [];
var forms_changed = [];
for (y=0;y<$('.mdc-layout-grid__inner').length;y++) {
    forms_changed.push('F');
    fields_memo.push(new Object());
    select_menus.push(new Object());
    chipsets.push(new Object())
    checkboxes.push(new Object())
}

$(window).on('login', function () {
	alert_opt[2]['message'] = alert_opt[2]['message']+CURRENT_NAME+'. Авторизация прошла успешно';
	callAlert(2)
}).on('logout', function () {
    var str = alert_opt[2]['message'];
	alert_opt[2]['message'] = str.replace(str.split(", ")[1],'');
    if ($('.mdc-layout-grid__inner').hasClass('editing')) location.reload()
});

$(document).ready(function() {
    animateSlides();
    headingSizer();

    $('.go-back').click(function(){window.close()});
    $('#submit-it').click(function(){
        $('#check-forms').val(forms_changed.join(''));
        $('.card--form').submit()
    });

    function whereAmI(el) {
        var elClasses = $(el).parents(".mdc-layout-grid__inner").attr('class').split (' ');
        for (var index in elClasses) {
            if (elClasses[index].match ( /^section\d+$/ ) ) {
                var classNum = parseInt(elClasses[index].split('tion')[1]);
                break
            }
        }
        return classNum
    }

    $.each($('.mdc-select'), function (i, el){
        var obj = new MDCSelect(el);
        var inp = $(el).parent().children('input');
        
        obj.value = inp.val();
        obj.listen('change', function (t) { inp.val(t.target.value) });
        obj.disabled = true;

        fields_memo[whereAmI(el)][inp.attr("name")]=inp.val();
        select_menus[whereAmI(el)][inp.attr("name")] = obj
    });
    $.each($('.mdc-checkbox'), function (i, el){
        var obj = new MDCCheckbox(el);
        if ($(el).index() > 1) var inp = $(el).parent().parent().children('input:last-of-type');
        else var inp = $(el).parent().parent().children('input:first-of-type');
        var init = inp.attr('possible').toLowerCase();
        
        if (inp.val().toLowerCase().indexOf(init) >= 0) obj.checked = true
        else obj.checked = false;
        obj.foundation_.adapter_.registerChangeHandler(function(t) { 
            if (t.target.checked) inp.val(inp.attr('possible')).trigger('change')
            else inp.val('').trigger('change')
        });
        obj.disabled = true;

        fields_memo[whereAmI(el)][inp.attr("name")]=inp.val();
        checkboxes[whereAmI(el)][inp.attr("name")] = obj
    });
    $.each($('.mdc-chip-set'), function (i, el){
        var obj = new MDCChipSet(el);
        var inp = $(el).parent().children('input');
        var init = inp.val().toLowerCase();
        
        obj.chips[0].foundation.adapter_.notifyInteraction();
        obj.chips[1].foundation.adapter_.notifyInteraction();
        if (init.indexOf('да') >= 0) obj.foundation_.select(obj.chips[0].foundation)
        else if (init.indexOf('нет') >= 0) obj.foundation_.select(obj.chips[1].foundation);

        obj.listen('MDCChip:interaction', function (t) {
            if (t.detail.chip.foundation.adapter_.hasClass('mdc-chip--selected')) inp.val(t.detail.chip.root_.innerText.toUpperCase()).trigger('change')
            else inp.val('').trigger('change')
        });
        $(el).addClass('choice-field-disabled');

        fields_memo[whereAmI(el)][inp.attr("name")]=inp.val();
        chipsets[whereAmI(el)][inp.attr("name")] = obj
    });
    [].forEach.call(document.querySelectorAll('.mdc-text-field'), mdc.textField.MDCTextField.attachTo);
    [].forEach.call(document.querySelectorAll('.mdc-icon-toggle:not(#user-tab)'), mdc.iconToggle.MDCIconToggle.attachTo);

    alert_opt.push(
		{ message: "Изменения сохранены", timeout: 2500,
		actionText: ''},
		{ message: "У вас нет доступа к этому разделу", timeout: 15000,
        actionText: 'Ошибка', actionHandler: function () {console.log('[No rights] alert is pressed')} },
        { message: "С возвращением, ", timeout: 2500,
		actionText: ''}
	)
});

function animateSlides() {
    card_nav = new MDCTabBar(document.querySelector('#card--pages-nav'));
    slides = $('.mdc-layout-grid__inner');
    lastTabInd = card_nav.activeTabIndex;

    card_nav.listen('MDCTabBar:change', function (t) {
        var ind = t.detail.activeTabIndex;
        var last = $(slides[lastTabInd]);
        if (ind == 4) {
            card_nav.activeTabIndex = lastTabInd;
            return
        }
        var current = $(slides[ind]);
        function slider(i, content) {
            if (diff<=1) {
                $('.silent').removeClass('silent');
                return
            }
            $(slides[i]).addClass('silent').toggleClass(content);
            setTimeout(function() {diff--; slider(i+1, content)}, 20)
        }

        if (last.height() > current.height()) var tabMinHeight = last.height()+50
        else var tabMinHeight = current.height()+50;
        $('.mdc-layout-grid').css('minHeight', tabMinHeight);

        last.addClass('slide-intermediate');
        var diff = Math.abs(ind-lastTabInd);

        if (ind > lastTabInd) {
            if (diff > 1) slider(lastTabInd+1, 'right-curtain left-curtain');
            last.toggleClass('left-curtain');
            current.toggleClass('right-curtain')
        } else {
            if (diff > 1) slider(ind+1, 'left-curtain right-curtain');
            last.toggleClass('right-curtain');
            current.toggleClass('left-curtain')
        }

        if (!current.hasClass('editing') && last.hasClass('editing')) {
            $('#edit_it').removeClass("mdc-fab--exited");
            $('.checkout, .card--form').removeClass('editing')
        } else if (current.hasClass('editing') && !last.hasClass('editing')) {
            $('#edit_it').addClass("mdc-fab--exited");
            $('.checkout, .card--form').addClass('editing')
        }

        setTimeout(function() {
            current.removeClass('slide-intermediate');
            lastTabInd = ind;
            $('.mdc-layout-grid').css('minHeight', '')
        }, 350)
    });
}

function headingSizer() {
    var base = $('.card--heading');
    var el = base.children('span');

    base.addClass('card--heading-size0')
    if (el.width() < 0.75*950 && base.height()/parseFloat(base.css('line-height')) < 2) {
        base.removeClass('card--heading-modifying');
        return
    } else base.removeClass('card--heading-size0')
    
    for (z=1;z<4;z++) {
        base.addClass('card--heading-size'+z)
        if (Math.round(base.height()/parseFloat(base.css('line-height'))) < (z+1)) {
            base.removeClass('card--heading-modifying');
            return
        } else base.removeClass('card--heading-size'+z)
    }

    base.addClass('card--heading-size4');
    base.removeClass('card--heading-modifying')
}

function edit() {
    var card_ind_now = card_nav.activeTabIndex;
    if (!checkAuth()) {
        showLogin();
        return
    } else if (checkRights(card_ind_now)) {
        var selector = '.section'+card_ind_now;
        $('#edit_it').toggleClass("mdc-fab--exited");

        $(selector+' input').attr('readonly', false);
        $(selector+' input').not("[name='csrfmiddlewaretoken']").not("[type='checkbox']").focus(function(){
            if (typeof(fields_memo[card_ind_now][$(this).attr("name")]) == 'undefined') {
                fields_memo[card_ind_now][$(this).attr("name")]=$(this).val()
            }
        }).change(function(){
            if (fields_memo[card_ind_now][$(this).attr("name")] == $(this).val()) forms_changed[card_ind_now] = "F"
            else forms_changed[card_ind_now] = "T"
        });

        $(selector+' [data-toggle="datepicker"]').each(function() {
            $(this).datepicker({
                autoHide: true,
                container: 'main',
                weekStart: 1,
                disabledClass: 'calendar-disabled',
                trigger: $(this).closest('.custom-text-field-with-icon').children('i'),
                language: 'ru-RU',
                format: 'dd.mm.yyyy'
            })
        });

        $.each($(selector+' .custom-integer'), function (i, el){
            var switchers = $(el).children('i');
            var inp = $(el).children('div').children('input');
            fields_memo[card_ind_now][inp.attr("name")]=inp.val();
            var loopthis;
            function changeVal(v, bigger) {
                if (isNaN(parseInt(v.val()))) v.val(0);
                if (bigger) v.val(parseInt(v.val())+1).trigger('change')
                else if (parseInt(v.val()) > 0) v.val(parseInt(v.val())-1).trigger('change')
            }
            $(switchers[0]).mousedown(function () {changeVal(inp, false); loopthis = setInterval(changeVal, 200, inp, false)
            }).mouseup(function () {clearInterval(loopthis)});
            $(switchers[1]).mousedown(function () {changeVal(inp, true); loopthis = setInterval(changeVal, 200, inp, true)
            }).mouseup(function () {clearInterval(loopthis)});
        });

        $.each(select_menus[card_ind_now], function (i, el){ el.disabled = false });
        $.each(checkboxes[card_ind_now], function (i, el){ el.disabled = false });
        $.each(chipsets[card_ind_now], function (i, el){ $(el.root_).removeClass('choice-field-disabled') });

        $.each($(selector+' .clear-field'), function (i, el){
            var inp = $(el).parent().children('div').children('input');
            $(el).click(function (){inp.val('')})
        });

        setTimeout(function() {
            $(selector+', .checkout, .card--form').addClass('editing');
        }, 100)
    } else callAlert(1)
}

function checkRights(section) {
    var result = false;
    $.ajax({
        url: '/check_rights/',
        type: 'POST',
        data: {
            'send': section
        },
        dataType: 'json',
        async: false,
        success: function (data) {
            if (data.has_rights) result = true
        }
    })
    return result
}