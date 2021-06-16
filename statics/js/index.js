$(function() {
    function search_func(event) {
        event.preventDefault();
        $.ajax({
            method: "POST",
            url: "/search",
            data: {
                "query": $("#search_input").val()
            },
            success: function(response) {
                // console.log(response);
                var list = "";
                var flag = true;
                console.log(response.data);
                var index = Object.keys(response.data).sort(function(a, b) { 
                    return Object.keys(response.data[b]).length - Object.keys(response.data[a]).length; 
                });
                console.log(index);
                for (var i in index) {
                    list += "<li style='list-style: none;'><a class='from'>Document " + index[i].toString() + " (" + Object.keys(response.data[index[i]]).length
                    + ")</a><ul class='list-group'>";
                    for (var ans in response.data[index[i]]) {
                        var tmp = response.data[index[i]][ans];
                        if (tmp[0] != '#') {
                            tmp = "... " + tmp + " ...";
                        }
                        list += "<a class='list-group-item list-group-item-action'>" + tmp + "</a>";
                    }
                    list += "</ul></li>";
                    flag = false;
                }
                if (flag) {
                    list = "No result found !";
                }
                $("#result_list").hide()
                $("#result_list").html(list);
                $("#result_list").fadeIn(500);
                $('#search_input').focus().select();
                logs = "<p><span class='time'>[" + response.time.toString() + "secs]</span> ";
                flag = false;
                hints = "For word <span class='wrong_word'>";
                for (var word in response.hint) {
                    hints += word + "</span>: Are you looking for ";
                    word_hint = "";
                    for (var w in response.hint[word]) {
                        word_hint += "<strong>" + response.hint[word][w] + "</strong>, ";
                    }
                    hints += word_hint + "? ";
                    flag = true;
                }
                if (flag) logs += hints;
                logs += "</p>";
                $(".main .hint").html(logs);
                return false;
            }
        });
    }
    $('#search_input').bind('keypress', function(event) {
        if (event.keyCode == "13") {
            search_func(event);
        }
    });
    $("#search_btn").click(function(event) {
        search_func(event);
    });
});