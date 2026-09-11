import QtQuick 2.15
import QtQuick.Controls 2.15

// Animação de Progresso - Barra Gradiente
// Template 2: Barra Horizontal com Gradiente Animado

Rectangle {
    id: root
    width: 400
    height: 60
    color: "transparent"
    
    property real progressValue: 0.0
    property color primaryColor: "#3498db"
    property color secondaryColor: "#2ecc71"
    property color gradientColor1: "#ff006e"
    property color gradientColor2: "#8338ec"
    
    // Fundo da barra
    Rectangle {
        anchors.fill: parent
        radius: 8
        color: "#ecf0f1"
        border.color: "#bdc3c7"
        border.width: 2
    }
    
    // Barra de progresso gradiente
    Rectangle {
        id: progressBar
        width: parent.width * progressValue
        height: parent.height - 4
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 2
        radius: 6
        
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: gradientColor1 }
            GradientStop { position: 0.5; color: "#fb5607" }
            GradientStop { position: 1.0; color: gradientColor2 }
            
            SequentialAnimation on GradientStop.position {
                target: gradientGradientStops[0]
                NumberAnimation { from: 0.0; to: 1.0; duration: 2000 }
                loops: Animation.Infinite
                running: true
            }
        }
        
        // Efeito de brilho
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: "#ffffff"; opacity: 0.3 }
                GradientStop { position: 0.5; color: "transparent" }
                GradientStop { position: 1.0; color: "#000000"; opacity: 0.1 }
            }
        }
        
        // Partículas animadas
        Repeater {
            model: 5
            Rectangle {
                width: 20
                height: parent.height / 2
                radius: 3
                color: "rgba(255, 255, 255, 0.4)"
                
                PropertyAnimation {
                    target: parent
                    property: "x"
                    from: -20
                    to: progressBar.width
                    duration: 1500 + index * 300
                    loops: Animation.Infinite
                    running: true
                }
            }
        }
    }
    
    // Texto de porcentagem
    Text {
        anchors.centerIn: parent
        text: Math.round(progressValue * 100) + "%"
        font.pixelSize: 24
        font.bold: true
        color: "#2c3e50"
        font.family: "Segoe UI"
        style: Text.Outline
        styleColor: "#ffffff"
    }
}
