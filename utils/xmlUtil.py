# -*- coding=utf-8 -*-

from xml.etree.ElementTree import ElementTree, Element
import xml.etree.ElementTree as ET
import jenkins
# credentials_id = cf.get("jenkins", "credentialsId")


class XmlUtil:

    @staticmethod
    def read_xml(in_path):
        """读取并解析xml文件
          in_path: xml路径
          return: ElementTree"""
        tree = ElementTree()

        tree.parse(in_path)
        return tree

    @staticmethod
    def write_xml(tree, out_path):
        """将xml文件写出
          tree: xml树
          out_path: 写出路径"""
        tree.write(out_path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def if_match(node, kv_map):
        """判断某个节点是否包含所有传入参数属性
          node: 节点
          kv_map: 属性及属性值组成的map"""
        for key in kv_map:
            if node.get(key) != kv_map.get(key):
                return False
        return True

    # ---------------search -----
    @staticmethod
    def find_nodes(tree, path):
        """查找某个路径匹配的所有节点
          tree: xml树
          path: 节点路径"""
        return tree.findall(path)

    @staticmethod
    def get_node_by_keyvalue(nodelist, kv_map):
        """根据属性及属性值定位符合的节点，返回节点
          nodelist: 节点列表
          kv_map: 匹配属性及属性值map"""
        result_nodes = []
        for node in nodelist:
            if XmlUtil.if_match(node, kv_map):
                result_nodes.append(node)
        return result_nodes

    # ---------------change -----
    @staticmethod
    def change_node_properties(nodelist, kv_map, is_delete=False):
        """修改/增加 /删除 节点的属性及属性值
          nodelist: 节点列表
          kv_map:属性及属性值map"""
        for node in nodelist:
            for key in kv_map:
                if is_delete:
                    if key in node.attrib:
                        del node.attrib[key]
                else:
                    node.set(key, kv_map.get(key))

    @staticmethod
    def change_node_text(nodelist, text, is_add=False, is_delete=False):
        """改变/增加/删除一个节点的文本
          nodelist:节点列表
          text : 更新后的文本"""
        for node in nodelist:
            if is_add:
                node.text += text
            elif is_delete:
                node.text = ""
            else:
                node.text = text

    @staticmethod
    def create_node(tag, property_map, content):
        """新造一个节点
          tag:节点标签
          property_map:属性及属性值map
          content: 节点闭合标签里的文本内容
          return 新节点"""
        element = Element(tag, property_map)
        element.text = content
        return element

    @staticmethod
    def add_child_node(nodelist, element):
        """给一个节点添加子节点
          nodelist: 节点列表
          element: 子节点"""
        for node in nodelist:
            node.append(element)

    @staticmethod
    def del_node_by_tagkeyvalue(nodelist, tag, kv_map):
        """同过属性及属性值定位一个节点，并删除之
          nodelist: 父节点列表
          tag:子节点标签
          kv_map: 属性及属性值列表"""
        for parent_node in nodelist:
            children = parent_node.getchildren()
            for child in children:
                if child.tag == tag and XmlUtil.if_match(child, kv_map):
                    parent_node.remove(child)

    @staticmethod
    def generate_xml(url, branch, pre_shell, pos_shell):

        # 1. 读取xml文件
        # tree = XmlUtil.read_xml("../static/xml/empty.xml")
        # print(jenkins.EMPTY_CONFIG_XML)
        tree = ET.fromstring(jenkins.EMPTY_CONFIG_XML)



        # 2. 属性修改
        # A. 找到父节点
        scm = XmlUtil.find_nodes(tree, "scm")
        # B. 通过属性准确定位子节点
        # result_nodes = get_node_by_keyvalue(nodes, {"class": "BProcesser"})
        # C. 修改节点属性
        XmlUtil.change_node_properties(scm, {"class": "hudson.plugins.git.GitSCM"})
        # D. 删除节点属性
        XmlUtil.change_node_properties(scm, {"plugin": "git@2.5.3"})

        # 3. 节点修改
        # 在SCM节点下增加子节点
        XmlUtil.add_child_node(scm, XmlUtil.create_node("configVersion", {}, str(2)))
        XmlUtil.add_child_node(scm, XmlUtil.create_node("userRemoteConfigs", {}, ""))
        XmlUtil.add_child_node(scm, XmlUtil.create_node("branches", {}, ""))
        XmlUtil.add_child_node(scm, XmlUtil.create_node("doGenerateSubmoduleConfigurations", {}, "false"))
        XmlUtil.add_child_node(scm, XmlUtil.create_node("submoduleCfg", {"class": "list"}, ""))
        XmlUtil.add_child_node(scm, XmlUtil.create_node("extensions", {}, ""))
        # 在userRemoteConfigs节点下增加子节点
        userRemoteConfigs = XmlUtil.find_nodes(tree, "scm/userRemoteConfigs")
        XmlUtil.add_child_node(userRemoteConfigs, XmlUtil.create_node("hudson.plugins.git.UserRemoteConfig", {}, ""))
        UserRemoteConfig = XmlUtil.find_nodes(tree, "scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig")
        XmlUtil.add_child_node(UserRemoteConfig, XmlUtil.create_node("url", {}, url))
        # XmlUtil.add_child_node(UserRemoteConfig, XmlUtil.create_node("credentialsId", {}, credentials_id))
        # 在branches节点下增加子节点
        branches = XmlUtil.find_nodes(tree, "scm/branches")
        XmlUtil.add_child_node(branches, XmlUtil.create_node("hudson.plugins.git.BranchSpec", {}, ""))
        BranchSpec = XmlUtil.find_nodes(tree, "scm/branches/hudson.plugins.git.BranchSpec")
        XmlUtil.add_child_node(BranchSpec, XmlUtil.create_node("name", {}, branch))

        properties = XmlUtil.find_nodes(tree, "properties")
        XmlUtil.add_child_node(properties, XmlUtil.create_node(
            "com.dabsquared.gitlabjenkins.connection.GitLabConnectionProperty", {"plugin": "gitlab-plugin@1.3.0"}, ""))

        GitLabConnectionProperty = XmlUtil.find_nodes(tree,
                                              "properties/com.dabsquared.gitlabjenkins.connection.GitLabConnectionProperty")
        gitLabConnection = XmlUtil.create_node("gitlab", {}, "gitlab")
        XmlUtil.add_child_node(GitLabConnectionProperty, gitLabConnection)

        builders = XmlUtil.find_nodes(tree, "builders")
        XmlUtil.add_child_node(builders, XmlUtil.create_node("hudson.tasks.Shell", {}, ""))
        XmlUtil.add_child_node(builders, XmlUtil.create_node("hudson.tasks.Maven", {}, ""))
        XmlUtil.add_child_node(builders, XmlUtil.create_node("hudson.tasks.Shell", {}, ""))

        maven = XmlUtil.find_nodes(tree, "builders/hudson.tasks.Maven")
        XmlUtil.add_child_node(maven, XmlUtil.create_node("targets", {}, "clean install"))
        XmlUtil.add_child_node(maven, XmlUtil.create_node("mavenName", {}, "maven"))
        XmlUtil.add_child_node(maven, XmlUtil.create_node("usePrivateRepository", {}, "false"))
        XmlUtil.add_child_node(maven, XmlUtil.create_node("settings",
                                                          {"class": "jenkins.mvn.DefaultSettingsProvider"}, ""))
        XmlUtil.add_child_node(maven, XmlUtil.create_node("globalSettings",
                                                          {"class": "jenkins.mvn.DefaultGlobalSettingsProvider"}, ""))

        shell = XmlUtil.find_nodes(tree, "builders/hudson.tasks.Shell")
        shell[0].append(XmlUtil.create_node("command", {}, pre_shell))
        shell[1].append(XmlUtil.create_node("command", {}, pos_shell))

        # 定位父节点
        # del_parent_nodes = find_nodes(tree, "processers/services/service")
        # 准确定位子节点并删除之
        # target_del_node = del_node_by_tagkeyvalue(del_parent_nodes, "chain", {"sequency": "chain1"})

        # 5. 修改节点文本
        # 定位节点
        # text_nodes = get_node_by_keyvalue(find_nodes(tree, "processers/services/service/chain"), {"sequency": "chain3"})
        # change_node_text(text_nodes, "new text")

        # 6. 输出到结果文件
        # XmlUtil.write_xml(tree, "../static/xml/new_config.xml")

        config = ET.tostring(tree)
        return config

if __name__ == '__main__':
    XmlUtil.generate_xml("git@gitlab.vomoho.com:moho_web/vomoho-fetch.git", "*/develop_fetch")
