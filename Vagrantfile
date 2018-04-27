# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.provider "virtualbox" do |vb|
  #   vb.gui = true
    vb.memory = "256"
    vb.cpus = 1
  end

  config.vm.define "u1" do | u1 |
    u1.vm.box = "ubuntu/xenial64"
    u1.vm.network "private_network", ip: "10.0.0.11"
    u1.vm.hostname = "u1"
    config.ssh.insert_key = false
  end

  config.vm.provision "shell", inline: <<-SHELL
    date
    echo Done!
  SHELL
end