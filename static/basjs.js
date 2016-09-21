

    function bindText(){
        $('#manager').on('input propertychange', show_manager);
        $('#member').on('input propertychange', show_member);
    }

    function bindLi(){
        $("#managerbox").children().children("li").on('click', function(){
            setManagerValue($(this).text());
        });
        $("#memberbox").children().children("li").on('click', function(){
            setMemberValue($(this).text());
        });
    }

    function show_manager(){
        var s_value = $("#manager").val().trim();
        $("#managerbox").children().children("li").hide();
        var flag = false;
        if(s_value.length >= 1){
            $("#managerbox").children().children("li").each(function(){
                if(s_value==$(this).text().substr(0,s_value.length)){
                        flag = true;
                        $(this).show();
                }
            });
            if(flag===true){
                $("#managerbox").css("display","block");
            } else {
                hide();
            }
        } else {
            hide();
        }
    }

    function show_member(){
        var s_value = $("#member").val().trim();
        $("#memberbox").children().children("li").hide();
        var flag = false;
        if(s_value.length >= 1){
            $("#memberbox").children().children("li").each(function(){
                if(s_value==$(this).text().substr(0,s_value.length)){
                        flag = true;
                        $(this).show();
                }
            });
            if(flag===true){
                $("#memberbox").css("display","block");
            } else {
                hide();
            }
        } else {
            hide();
        }
    }

    function hide(){
        $(".userbox").css("display","none");
    }

    function setManagerValue(str){
        $("#manager").val(str);
        hide();
    }

    function setMemberValue(str){
        $("#member").val(str);
        hide();
    }

    function project_add(){
        var project_name = $(this).children("div:eq(0)").children("input").val();
        var gitlab_url = $(this).children("div:eq(1)").children("input").val();
        var branch = $(this).children("div:eq(2)").children("input").val();
        var message = "";
        if(project_name!="" && gitlab_url!="" && branch!=""){
            return true;
        } else{
            if(project_name==""){
                message = message + "工程名不能为空" + "\n";
            }
            if(gitlab_url==""){
                message = message + "gitlab地址不能为空" + "\n";
            }
            if(branch==""){
                message = message + "分支不能为空";
            }
            alert(message);
            return false;
        }
    }

    var deploy_add = function (){
        var project = $(this).children("div:eq(0)").children("select").val();
        var server = $(this).children("div:eq(1)").children("select").val();
        var cycle = $(this).children("div:eq(2)").children("select").val();
        var reviewer = $(this).children("div:eq(3)").children("select").val();
        var message = "";
        if(project!="" && server!="" && cycle!="" && reviewer != ""){
            return true;
        } else{
            if(project==""){
                message = message + "请选择一个工程" + "\n";
            }
            if(server==""){
                message = message + "请选择一个服务器" + "\n";
            }
            if(cycle==""){
                message = message + "请选择一个迭代周期" + "\n";
            }
            if(reviewer==""){
                message = message + "请选择一个审核者";
            }
            alert(message);
            return false;
        }
    }

    var refuse = function(){
        var deploy_id = $(this).parent().parent().children("input").val();
        $("#modal2_deploy_id").val(deploy_id);
        $("#reply").val(1);

    };

    var approved =  function(){
        var deploy_id = $(this).parent().parent().children("input").val();
        $("#modal2_deploy_id").val(deploy_id);
        $("#reply").val(0);

    };

    var submit_modal = function(){
        var modal2_deploy_id = $("#modal2_deploy_id").val();
        var reply = $("#reply").val();
        var comment = $("#comment").val();
        if(reply === '0'){
          $.post("/deploy/deploy_approved", { deploy_id: modal2_deploy_id, comment: comment},
          function(data){
            var obj = JSON.parse(data['result']);
                if(obj.result == 200){
                    window.location.reload();
                }
          });
        } else {
          $.post("/deploy/deploy_refuse", { deploy_id: modal2_deploy_id, comment: comment},
          function(data){
            var obj = JSON.parse(data['result']);
                if(obj.result == 200){
                    window.location.reload();
                }
          });
        }
    }

    var build = function(){
        var deploy_id = $(this).parent().parent().children("input").val();
        var project_name = $(this).parent().parent().children("td:eq(1)").text();
        $.post("/deploy/build_jenkins", { project_name: project_name, deploy_id: deploy_id },
          function(data){
            var obj = JSON.parse(data['result']);
                if(obj.result == 200){
                    window.location.reload();
                }
          });
    };

    var deploy = function(){
        var deploy_id = $("#modal_deploy_id").val();
        var env_name = $("#modal_env_name").val();
        $.post("/deploy/deploy_launch", {deploy_id: deploy_id, env_name: env_name},
            function(data){
                var obj = JSON.parse(data['result']);
                if (obj.result == 200) {
                    window.location.reload();
                }
            }
        );
    };

    var deploy_modal = function(){
        var deploy_id = $(this).parent().parent().children("input").val();
        $("#modal_deploy_id").val(deploy_id);
    }

    var deploy_delete = function(){
        var deploy_id = $(this).parent().parent().children("input").val();
        $.post("/deploy/deploy_delete", { deploy_id: deploy_id },
          function(data){
            var obj = JSON.parse(data['result']);
                if(obj.result == 200){
                    window.location.reload();
                }
          });
    };

    var store = function(){
        var deploy_id = $(this).parent().parent().children("input").val();
        $.post("/deploy/deploy_store", { deploy_id: deploy_id },
          function(data){
            var obj = JSON.parse(data['result']);
                if(obj.result == 200){
                    window.location.reload();
                }
          });
    };

    var find_manager = function(){
        var project_name = $("#select_project").val();
        if($(this).val() == ''){
          return;
        }
        else{
          $.post("/deploy/select_project", { project_name: project_name },
          function(data){
            var option = '<option></option>';
            var obj = JSON.parse(data['result']);
            for(var i = 0;i < obj.result.length; i++){
                option = option + "<option>"+ obj.result[i] +"</option>";
            }
            $("#review_develop").html(option);
          });
        }
    };