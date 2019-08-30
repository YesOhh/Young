$(function () {
    var default_error_message = 'Server error, please try again later.';


    function render_time(){
        return moment($(this).data('timestamp')).format('lll')
    }

    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    )

    function myFunction(){
	    document.getElementById("demo").innerHTML="取消关注";
    }


});
