jQuery(function(e){Stripe.setPublishableKey(config.publishable_key);+function(){if(e(window).width()<1e3)return;var t=e("#tabs").addClass("js"),n=t.find(".tab").hide(),r=t.find(".selector");e(window).resize(function(){e(window).width()<1e3?t.removeClass("js"):t.addClass("js")});r.first().addClass("active");n.first().fadeIn();r.mouseenter(function(){var t=e(this);r.filter(".active").removeClass("active");n.stop(!0,!0).fadeOut();t.next(".tab").stop(!0,!0).fadeIn();t.addClass("active")})}();+function(){function l(){var t=e(".screen.active");t.removeClass("active");t.next(".screen").addClass("active")}function c(t){d(o);if(t=="OK"){e("#samedata").is(":checked")&&u.find("input.email").first().val(o.find("input.email").val());l()}else m(o,'Ocurrió un error en el proceso. Por favor intentalo más tarde o escribenos a <a href="mailto:ventas@mejorando.la">ventas@mejorando.la</a>.')}function h(e){d(u);if(e=="OK"){r.addClass("success").html(":) Felicidades");t.html('<div class="final"><p>Ya estás listo para asistir a este curso:</p><h1>'+config.nombre+'</h1><div class="pago-links"><p>Te invitamos a saber más de nuestros</p><a href="http://mejorando.la/cursos" target="_blank"><button>Cursos</button></a><a href="http://mejorando.la/videos" target="_blank"><button>Videos</button></a></div></div>')}else m(u,'Ocurrió un error en el proceso. Por favor intentalo más tarde o escribenos a <a href="mailto:ventas@mejorando.la">ventas@mejorando.la</a>.')}function p(e){e.addClass("sending");v(e,"Enviando...")}function d(e){e.removeClass("sending");v(e,"")}function v(e,t){e.find(".notice").html(t);return!1}function m(e,t){e.find(".notice").html('<span class="err">*</span> '+t);return!1}function g(t,n){t.find('input[type="text"]').each(function(){var t=e(this);if(!n&&t.attr("name")==undefined)return;t.removeClass("error");t.val().match(/^\s*$/)&&t.addClass("error")});return t.find(".error").size()>0?!1:!0}function y(){var e=Math.floor(i/5),t=s*i,n=e*s;i%5!==0&&(n+=s*.1*(i<5?i-1:i-5*e));t-=n;n=Math.ceil(n);t=Math.ceil(t);var o="";n>0&&(o=" <span>con un descuento de <strong>$"+n+" USD</strong></span>");r.html("$"+t+" USD"+o)}function b(){var e=u.find(".alumnos"),t="";for(var n=1;n<=i;n++)t+='<label class="alumno">Alumno '+n+': <input type="text" placeholder="Email" class="email"   name="email" /></label>';e.html(t)}var t=e(".screens"),n=t.find(".screen"),r=e("#pago-status"),i=1,s=parseInt(config.precio),o=e("#buy-form"),u=e("#reg-form"),a=o.find('input[name="quantity"]');e(".pago-count a").live("click",function(){var t=e(this);if(t.is(".pago-mas"))i++;else{if(i==1)return;i--}a.val(i);e(".pago-num").html(i);y();b()});e(".pago-btns .next").live("click",l);var f={incorrect_number:"El número de tarjeta es incorrecto",invalid_number:"El número de tarjeta no es un número real o está mal escrito",invalid_expiry_month:"La fecha de expiración de la tarjeta es invalida",invalid_expiry_year:"El año de expiración de la tarjeta es invalido",invalid_cvc:"El código de seguridad de la tarjeta no es el correcto",expired_card:"Tu tarjeta expiró",incorrect_cvc:"El código de seguridad de la tarjeta no es el correcto",card_declined:"Tu tarjeta fue rechazada (intenta con otra)",processing_error:"Un error ocurrió mientras procesabamos tu tarjeta, intenta de nuevo"};o.submit(function(){if(!g(o,!0))return m(o,"Debe completar todos los campos.");p(o);Stripe.createToken({number:o.find(".card-number").val(),cvc:o.find(".card-cvc").val(),exp_month:o.find(".card-expiry-month").val(),exp_year:o.find(".card-expiry-year").val()},function(t,n){d(o);if(n.error){var r=n.error.message;f[n.error.code]&&(r=f[n.error.code]);m(o,r)}else{o.find('input[name="stripeToken"]').val(n.id);p(o);e.post(o.attr("action"),o.serialize(),c)}});return!1});u.submit(function(){if(!g(u))return m(u,"Debe completar todos los campos.");p(u);e.post(u.attr("action"),u.serialize(),h);return!1});e(".pago-btns .cancel").live("click",function(){e(".screen.active").removeClass("active");n.first().addClass("active")})}();e("#video-link").click(function(){e(this).html('<iframe width="666" height="376" src="http://www.youtube.com/embed/x4ZwpiKR7ew?autoplay=1&modestbranding=1&showinfo=0&autohide=1&controls=0" frameborder="0" allowfullscreen></iframe>');return!1});var t=new function(){var t=e("#pago"),n=t.find(".overlay");$panel=t.find(".panel");this.hide=function(){n.addClass("fadeOut");$panel.addClass("bounceOutUp");setTimeout(function(){t.removeClass("show");n.removeClass("fadeOut").removeClass("fadeIn");$panel.removeClass("bounceOutUp").removeClass("bounceInDown")},1010);return!1};this.show=function(){t.addClass("show");n.addClass("fadeIn");$panel.addClass("bounceInDown")};n.click(this.hide)};e(".close").click(t.hide);e("#registrate").click(t.show)});