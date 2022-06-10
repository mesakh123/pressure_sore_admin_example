

  $('form').submit(function(e) {
          e.preventDefault();

            $.ajax({

                url: "{% url 'demo:feedbacksubmit_url' %}",
                type: 'POST',
                data: {

                },
                cache: false,
                contentType: false,
                processData: false,
                complete: function(xmlHttp) {
                  // xmlHttp is a XMLHttpRquest object
                  $('form').each(function(){
                      //this.reset();   //Here form fields will be cleared.
                  });
                  if (xmlHttp.status == 200) {
                    top.location.href ="/demo/result/";
                  }
                  else{
                    top.location.href = '/demo/';
                  }
                }
            });

         };


  });
