
  window.addEventListener( "pageshow", function ( event ) {
    var historyTraversal = event.persisted ||
                           ( typeof window.performance != "undefined" &&
                                window.performance.navigation.type === 2 );
    if ( historyTraversal ) {
      // Handle page restore.
      window.location.reload();
    }
  });

  $('form').on('submit',function(e) {

        $("#progressIdinputData").show();
        document.getElementsByTagName('body')[0].setAttribute('style','overflow:hidden;') 

  });
  $(document).ready(function(){


    // Set the default value of each input

    // Functions to perform on click
    $('#clear').click(function(){
        // clear unchanged values
        $('input[type=text]').each(function(){
            if ($(this).val() == this.defaultValue) $(this).val('');
        });
    });
  });
