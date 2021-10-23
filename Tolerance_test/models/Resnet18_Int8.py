import torch.nn as nn
import math
import sys
import os

sys.path.append(os.getcwd())
from python.torx.module_Int8.layer import crxb_Conv2d
from python.torx.module_Int8.layer import crxb_Linear

__all__ = ['ResNet', 'resnet18', 'resnet34', 'resnet50', 'resnet101',
           'resnet152']



class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out

def conv3x3(in_planes, out_planes, stride=1):
    """3x3 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)

class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, 
                    crxb_size, gmin, gmax, gwire, gload, vdd, ir_drop, freq, temp, device, scaler_dw, enable_noise,
                    enable_SAF, enable_val_SAF,enable_ec_SAF, enable_resistance_variance, resistance_variance_gamma,
                    stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = crxb_Conv2d(inplanes, planes, kernel_size=3, stride=stride, padding=1, bias=False,
                                 crxb_size=crxb_size, scaler_dw=scaler_dw,
                                 gwire=gwire, gload=gload, gmax=gmax, gmin=gmin, vdd=vdd, freq=freq, temp=temp,
                                 enable_resistance_variance=enable_resistance_variance,
                                 resistance_variance_gamma=resistance_variance_gamma,
                                 enable_SAF=enable_SAF, enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF,
                                 enable_noise=enable_noise, ir_drop=ir_drop, device=device)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = crxb_Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False,
                                 crxb_size=crxb_size, scaler_dw=scaler_dw,
                                 gwire=gwire, gload=gload, gmax=gmax, gmin=gmin, vdd=vdd, freq=freq, temp=temp,
                                 enable_resistance_variance=enable_resistance_variance,
                                 resistance_variance_gamma=resistance_variance_gamma,
                                 enable_SAF=enable_SAF, enable_val_SAF=enable_val_SAF,enable_ec_SAF=enable_ec_SAF,
                                 enable_noise=enable_noise, ir_drop=ir_drop, device=device)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out

class ResNet(nn.Module):
    
    def __init__(self, block, layers, 
                crxb_size, gmin, gmax, gwire, gload, vdd, ir_drop, freq, temp, device, scaler_dw, enable_noise,
                 enable_SAF, enable_val_SAF, enable_ec_SAF, enable_resistance_variance, resistance_variance_gamma,
                    num_classes=1000):
        self.inplanes = 64
        super(ResNet, self).__init__()
        self.conv1 = crxb_Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False,
                        crxb_size=crxb_size, scaler_dw=scaler_dw,
                        gwire=gwire, gload=gload, gmax=gmax, gmin=gmin, vdd=vdd, freq=freq, temp=temp,
                        enable_resistance_variance=enable_resistance_variance,
                        resistance_variance_gamma=resistance_variance_gamma,
                        enable_SAF=enable_SAF, enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF,
                        enable_noise=enable_noise, ir_drop=ir_drop, device=device)

        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64,  layers[0], stride=1,
                    crxb_size=crxb_size, gmin=gmin, gmax=gmax, gwire=gwire, gload=gload, vdd=vdd, 
                    ir_drop=ir_drop, freq=freq, temp=temp, device=device, scaler_dw=scaler_dw, 
                    enable_resistance_variance=enable_resistance_variance,
                    resistance_variance_gamma=resistance_variance_gamma,
                    enable_noise=enable_noise,enable_SAF=enable_SAF, enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF)
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2,
                    crxb_size=crxb_size, gmin=gmin, gmax=gmax, gwire=gwire, gload=gload, vdd=vdd, 
                    ir_drop=ir_drop, freq=freq, temp=temp, device=device, scaler_dw=scaler_dw, 
                    enable_resistance_variance=enable_resistance_variance,
                    resistance_variance_gamma=resistance_variance_gamma,
                    enable_noise=enable_noise,enable_SAF=enable_SAF, enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2,
                    crxb_size=crxb_size, gmin=gmin, gmax=gmax, gwire=gwire, gload=gload, vdd=vdd, 
                    ir_drop=ir_drop, freq=freq, temp=temp, device=device, scaler_dw=scaler_dw,
                    enable_resistance_variance=enable_resistance_variance,
                    resistance_variance_gamma=resistance_variance_gamma, 
                    enable_noise=enable_noise,enable_SAF=enable_SAF, enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2,
                    crxb_size=crxb_size, gmin=gmin, gmax=gmax, gwire=gwire, gload=gload, vdd=vdd, 
                    ir_drop=ir_drop, freq=freq, temp=temp, device=device, scaler_dw=scaler_dw, 
                    enable_resistance_variance=enable_resistance_variance,
                    resistance_variance_gamma=resistance_variance_gamma,
                    enable_noise=enable_noise,enable_SAF=enable_SAF, enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF)
        self.avgpool = nn.AvgPool2d(7, stride=1)
        self.fc = crxb_Linear(512 * block.expansion, num_classes,
                            crxb_size=crxb_size, scaler_dw=scaler_dw,
                               gmax=gmax, gmin=gmin, gwire=gwire, gload=gload, freq=freq, temp=temp,
                               enable_resistance_variance=enable_resistance_variance,
                               resistance_variance_gamma=resistance_variance_gamma,
                               vdd=vdd, ir_drop=ir_drop, device=device, enable_noise=enable_noise,
                               enable_ec_SAF=enable_ec_SAF, enable_SAF=enable_SAF,enable_val_SAF=enable_val_SAF)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride,
                crxb_size, gmin, gmax, gwire, gload, vdd, ir_drop, freq, temp, device, scaler_dw, enable_noise,
                 enable_SAF, enable_val_SAF, enable_ec_SAF,enable_resistance_variance, resistance_variance_gamma):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                crxb_Conv2d(self.inplanes, planes * block.expansion, kernel_size=1, stride=stride, padding=0, bias=False,
                                 crxb_size=crxb_size, scaler_dw=scaler_dw,
                                 gwire=gwire, gload=gload, gmax=gmax, gmin=gmin, vdd=vdd, freq=freq, temp=temp,
                                 enable_resistance_variance=enable_resistance_variance,
                                 resistance_variance_gamma=resistance_variance_gamma,
                                 enable_SAF=enable_SAF, enable_val_SAF=enable_val_SAF,enable_ec_SAF=enable_ec_SAF,
                                 enable_noise=enable_noise, ir_drop=ir_drop, device=device),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride=stride, downsample=downsample, 
                        crxb_size=crxb_size, gmin=gmin, gmax=gmax, gwire=gwire, gload=gload, vdd=vdd, 
                        ir_drop=ir_drop, freq=freq, temp=temp, device=device, scaler_dw=scaler_dw,
                        enable_resistance_variance=enable_resistance_variance,
                        resistance_variance_gamma=resistance_variance_gamma, 
                        enable_noise=enable_noise,enable_SAF=enable_SAF,enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF))

        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes, stride=1, downsample=None,
                        crxb_size=crxb_size, gmin=gmin, gmax=gmax, gwire=gwire, gload=gload, vdd=vdd, 
                        ir_drop=ir_drop, freq=freq, temp=temp, device=device, scaler_dw=scaler_dw, 
                        enable_resistance_variance=enable_resistance_variance,
                        resistance_variance_gamma=resistance_variance_gamma,
                        enable_noise=enable_noise,enable_SAF=enable_SAF,enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)

        return x

def resnet50(pretrained=False, **kwargs):
    """Constructs a ResNet-50 model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = ResNet(Bottleneck, [3, 4, 6, 3], **kwargs)
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet50']))
    return model

def resnet18( crxb_size, gmin, gmax, gwire, gload, vdd, ir_drop, freq, temp, device, scaler_dw, enable_noise,
                 enable_SAF, enable_val_SAF,enable_ec_SAF,enable_resistance_variance, resistance_variance_gamma):
    """Constructs a ResNet-18 model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = ResNet(BasicBlock, [2, 2, 2, 2],
                    crxb_size=crxb_size, scaler_dw=scaler_dw,
                    gwire=gwire, gload=gload, gmax=gmax, gmin=gmin, vdd=vdd, freq=freq, temp=temp,
                    enable_resistance_variance=enable_resistance_variance,
                    resistance_variance_gamma=resistance_variance_gamma, 
                    enable_SAF=enable_SAF,enable_val_SAF=enable_val_SAF, enable_ec_SAF=enable_ec_SAF,
                    enable_noise=enable_noise, ir_drop=ir_drop, device=device)
    return model

def resnet101(pretrained=False, **kwargs):
    """Constructs a ResNet-101 model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = ResNet(Bottleneck, [3, 4, 23, 3], **kwargs)
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet101']))
    return model