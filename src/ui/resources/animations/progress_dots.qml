import QtQuick 2.15
import QtQuick.Controls 2.15

// Animação de Progresso - Pontos Pulsantes
// Template 3: Indicador de Carregamento com Dots

Rectangle {
    id: root
    width: 300
    height: 100
    color: "transparent"
    
    property real progressValue: 0.0
    property color dotColor: "#3498db"
    
    // Container dos pontos
    Row {
        anchors.centerIn: parent
        spacing: 15
        
        Repeater {
            model: 7
            Rectangle {
                id: dot
                width: 16
                height: 16
                radius: 8
                color: dotColor
                
                // Animação de pulso escalonado
                SequentialAnimation {
                    NumberAnimation {
                        target: dot
                        property: "scale"
                        to: 1.5
                        duration: 400
                        easing.type: Easing.OutQuad
                    }
                    NumberAnimation {
                        target: dot
                        property: "scale"
                        to: 1.0
                        duration: 400
                        easing.type: Easing.InQuad
                    }
                    PauseAnimation { duration: index * 100 }
                    loops: Animation.Infinite
                    running: true
                    startDelay: index * 100
                }
                
                // Opacidade baseada no progresso
                opacity: 0.3 + (progressValue * 0.7)
            }
        }
    }
    
    // Texto de porcentagem abaixo dos pontos
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.bottom
        anchors.topMargin: 10
        text: Math.round(progressValue * 100) + "% COMPLETO"
        font.pixelSize: 18
        font.bold: true
        color: dotColor
        font.family: "Segoe UI"
        letterSpacing: 2
        
        SequentialAnimation on opacity {
            NumberAnimation { from: 0.5; to: 1.0; duration: 800 }
            NumberAnimation { from: 1.0; to: 0.5; duration: 800 }
            loops: Animation.Infinite
            running: true
        }
    }
    
    // Linha de progresso sutil abaixo
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 3
        radius: 2
        
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: "transparent" }
            GradientStop { position: progressValue; color: dotColor }
            GradientStop { position: 1.0; color: "transparent" }
        }
    }
}
