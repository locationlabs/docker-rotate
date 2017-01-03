nodes = [
  { :hostname => 'vagrant-test-docker15',
    :ip => '172.16.218.2',
    :box => 'bento/ubuntu-14.04',
    :ram => 128,
    :cpus => 1,
    :docker_version => '1.5.0'},
  { :hostname => 'vagrant-test-docker19',
    :ip => '172.16.218.3',
    :box => 'bento/ubuntu-14.04',
    :ram => 128,
    :cpus => 1,
    :docker_version => '1.9.1'},
  { :hostname => 'vagrant-test-docker111',
    :ip => '172.16.218.4',
    :box => 'bento/ubuntu-14.04',
    :ram => 128,
    :cpus => 1,
    :docker_version => '1.11.2'},
  { :hostname => 'vagrant-test-docker112',
    :ip => '172.16.218.5',
    :box => 'bento/ubuntu-14.04',
    :ram => 128,
    :cpus => 1,
    :docker_version => '1.12.0'},
]
Vagrant.require_version ">= 1.6"
Vagrant.configure("2") do |config|
  config.ssh.insert_key = false

  if Vagrant.has_plugin?('vagrant-cachier')
    config.cache.enable :apt
  else
    printf("** Install vagrant-cachier plugin to speedup deploy: `vagrant plugin install vagrant-cachier`.**\n")
  end

  nodes.each do |node|
    config.vm.define node[:hostname] do |node_config|
      node_config.vm.box = node[:box]
      node_config.vm.host_name = node[:hostname]
      node_config.vm.network :private_network, ip: node[:ip]
      node_config.vm.provider :virtualbox do |vb|
        vb.memory = node[:ram]
        vb.cpus = node[:cpus]
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.customize ['guestproperty', 'set', :id, '/VirtualBox/GuestAdd/VBoxService/--timesync-set-threshold', 10000]
      end
      node_config.vm.provider "vmware_fusion" do |vb|
        vb.vmx["memsize"] = node[:ram]
        vb.vmx["numvcpus"] = node[:cpus]
      end
      node_config.vm.provision "shell", path: "vagrant/setup_docker.sh", args: node[:docker_version]
      node_config.vm.synced_folder "./", "/source" 
    end
  end
end


