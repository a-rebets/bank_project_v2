$(document).ready(function(){
                        var check = document.getElementById('id_zapros_o_predostavlenii_informacii');
                        if (check.checked) $('#div3').fadeIn('slow')
                        else $('#div3').fadeOut('slow');
                        $('#id_zapros_o_predostavlenii_informacii').change(function(){
                        if(this.checked) $('#div3').fadeIn('slow')
                        else $('#div3').fadeOut('slow');


                          });
                      });


$(document).ready(function(){
                        var check = document.getElementById('id_prepsanie_ob_ustranenii_narusheniya_zakonodatelstva_RF');
                        if (check.checked) $('#div5').fadeIn('slow')
                        else $('#div5').fadeOut('slow');
                          $('#id_prepsanie_ob_ustranenii_narusheniya_zakonodatelstva_RF').change(function(){
                              if(this.checked) $('#div5').fadeIn('slow')
                              else $('#div5').fadeOut('slow');


                          });
                      });


$(document).ready(function(){
                        var check = document.getElementById('id_predpisanie_ob_istrebovanii_documentov');
                        if (check.checked) $('#div4').fadeIn('slow')
                        else $('#div4').fadeOut('slow');
                          $('#id_predpisanie_ob_istrebovanii_documentov').change(function(){
                              if(this.checked) $('#div4').fadeIn('slow')
                              else $('#div4').fadeOut('slow');


                          });
                      });

$(document).ready(function(){
                        var check = document.getElementById('id_informaciaya_o_gosah_s_saitov_raskritiya_informacii');
                        if (check.checked) $('#div6').fadeIn('slow')
                        else $('#div6').fadeOut('slow');
                          $('#id_informaciaya_o_gosah_s_saitov_raskritiya_informacii').change(function(){
                              if(this.checked) $('#div6').fadeIn('slow')
                              else $('#div6').fadeOut('slow');


                          });
                      });

$(document).ready(function(){
                        var check = document.getElementById('id_zapros_o_predostavlenii_informacii_3_2');
                        if (check.checked) $('#div7').fadeIn('slow')
                        else $('#div7').fadeOut('slow');
                          $('#id_zapros_o_predostavlenii_informacii_3_2').change(function(){
                              if(this.checked) $('#div7').fadeIn('slow')
                              else $('#div7').fadeOut('slow');


                          });
                      });

$(document).ready(function(){
                        var check = document.getElementById('id_predpisanie_ob_istrebovanii_documentov_3_3');
                        if (check.checked) $('#div8').fadeIn('slow')
                        else $('#div8').fadeOut('slow');
                          $('#id_predpisanie_ob_istrebovanii_documentov_3_3').change(function(){
                              if(this.checked) $('#div8').fadeIn('slow')
                              else $('#div8').fadeOut('slow');


                          });
                      });

$(document).ready(function(){
                        var check = document.getElementById('id_polucheno_1_2_bool');
                        if (check.checked) $('#div9').fadeIn('slow')
                        else $('#div9').fadeOut('slow');
                          $('#id_polucheno_1_2_bool').change(function(){
                              if(this.checked) $('#div9').fadeIn('slow')
                              else $('#div9').fadeOut('slow');


                          });
                      });

$(document).ready(function(){
                        var check = document.getElementById('id_polucheno_1_3_bool');
                        if (check.checked) $('#div10').fadeIn('slow')
                        else $('#div10').fadeOut('slow');
                          $('#id_polucheno_1_3_bool').change(function(){
                              if(this.checked) $('#div10').fadeIn('slow')
                              else $('#div10').fadeOut('slow');


                          });
                      });






$(document).ready(function(){

	// $('.table').paging({limit:10});
	$('[data-toggle="tooltip"]').tooltip();

	 $(window).scroll(function(){
      if ($(this).scrollTop() > 300) {
        $('.scrollToTop').fadeIn();
      } else {
        $('.scrollToTop').fadeOut();
      }
    });


   NProgress.start();
   NProgress.done();

	 $('.scrollToTop').click(function(){
      $('html, body').animate({scrollTop : 0},800);
      return false;
    });

   $('ul.nav li.dropdown').hover(function() {
        $(this).find('.dropdown-menu').stop(true, true).delay(300).slideDown(300);
      }, function() {
        $(this).find('.dropdown-menu').stop(true, true).delay(300).slideUp(300);
      });

   $('#pannel').accordion({collapsible: true},{heightStyle: "content"}, {active: true});

   // $(function() { $("#id_leave_periods").daterangepicker(); });

   // Pagination Script
    $('.table').paging({limit:15});
    // END Pagination Script




   $('#accordion').accordion({
        collapsible:true,
        beforeActivate: function(event, ui) {
             // The accordion believes a panel is being opened
            if (ui.newHeader[0]) {
                var currHeader  = ui.newHeader;
                var currContent = currHeader.next('.ui-accordion-content');
             // The accordion believes a panel is being closed
            } else {
                var currHeader  = ui.oldHeader;
                var currContent = currHeader.next('.ui-accordion-content');
            }
             // Since we've changed the default behavior, this detects the actual status
            var isPanelSelected = currHeader.attr('aria-selected') == 'true';
            
             // Toggle the panel's header
            currHeader.toggleClass('ui-corner-all',isPanelSelected).toggleClass('accordion-header-active ui-state-active ui-corner-top',!isPanelSelected).attr('aria-selected',((!isPanelSelected).toString()));
            
            // Toggle the panel's icon
            currHeader.children('.ui-icon').toggleClass('ui-icon-triangle-1-e',isPanelSelected).toggleClass('ui-icon-triangle-1-s',!isPanelSelected);
            
             // Toggle the panel's content
            currContent.toggleClass('accordion-content-active',!isPanelSelected)    
            if (isPanelSelected) { currContent.slideUp(); }  else { currContent.slideDown(); }

            return false; // Cancels the default action
        }
    });

   $('#nomer_predpisaniya_po_reestru').keyup(function() {
  
  // If value is not empty
  if ($(this).val().length == 0) {
    // Hide the element
    $('.show_hide').hide();
  } else {
    // Otherwise show it
    $('.show_hide').show();
  }
  }).keyup(); // Trigger the keyup event, thus running the handler on page load

});

