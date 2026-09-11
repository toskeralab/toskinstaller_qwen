import QtQuick 2.15
import QtQuick.Controls 2.15

// Animação de Progresso - ToskeraLAB Edition
// Template 5: Tema oficial com gradientes e efeitos especiais

Rectangle {
    id: root
    width: 350
    height: 200
    color: "transparent"
    
    property real progressValue: 0.0
    property color toskPink: "#ff006e"
    property color toskPurple: "#8338ec"
    property color toskCyan: "#00f5d4"
    property color toskOrange: "#fb5607"
    
    // Fundo com gradiente sutil
    Rectangle {
        anchors.fill: parent
        radius: 15
        gradient: Gradient {
            orientation: Gradient.Vertical
            GradientStop { position: 0.0; color: "#0a0a0f"; opacity: 0.8 }
            GradientStop { position: 1.0; color: "#1a1a2e"; opacity: 0.9 }
        }
        border.width: 2
        border.color: toskPurple
    }
    
    // Barra de progresso principal com gradiente Toskera
    Rectangle {
        id: progressBar
        x: 20
        y: 40
        width: (parent.width - 40) * progressValue
        height: 40
        radius: 8
        
        visible: progressValue > 0
        
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: toskPink }
            GradientStop { position: 0.25; color: toskOrange }
            GradientStop { position: 0.5; color: "#ffbe0b" }
            GradientStop { position: 0.75; color: toskCyan }
            GradientStop { position: 1.0; color: toskPurple }
        }
        
        // Efeito de brilho interno
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: "#ffffff"; opacity: 0.4 }
                GradientStop { position: 0.4; color: "transparent" }
                GradientStop { position: 0.6; color: "transparent" }
                GradientStop { position: 1.0; color: "#000000"; opacity: 0.2 }
            }
        }
        
        // Partículas brilhantes animadas
        Repeater {
            model: 8
            Rectangle {
                width: 25 + Math.random() * 15
                height: parent.height * (0.3 + Math.random() * 0.4)
                radius: 3
                color: "rgba(255, 255, 255, 0.5)"
                
                PropertyAnimation {
                    target: parent
                    property: "x"
                    from: -30
                    to: progressBar.width + 30
                    duration: 2000 + Math.random() * 1000
                    loops: Animation.Infinite
                    running: true
                    startDelay: Math.random() * 2000
                }
            }
        }
    }
    
    // Container do texto de porcentagem
    Rectangle {
        anchors.centerIn: parent
        width: percentageText.implicitWidth + 40
        height: percentageText.implicitHeight + 20
        radius: 10
        color: "#1a1a2e"
        border.width: 2
        border.color: progressValue >= 1.0 ? toskCyan : toskPink
        
        Text {
            id: percentageText
            anchors.centerIn: parent
            text: Math.round(progressValue * 100) + "%"
            font.pixelSize: 42
            font.bold: true
            font.family: "Segoe UI"
            
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: toskPink }
                GradientStop { position: 0.5; color: toskCyan }
                GradientStop { position: 1.0; color: toskPurple }
            }
            
            SequentialAnimation on scale {
                NumberAnimation { from: 1.0; to: 1.15; duration: 400; easing.type: Easing.OutQuad }
                NumberAnimation { from: 1.15; to: 1.0; duration: 400; easing.type: Easing.InQuad }
                loops: Animation.Infinite
                running: true
            }
        }
    }
    
    // Logo/texto ToskeraLAB abaixo
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 15
        text: "TOSKINSTALLER"
        font.pixelSize: 16
        font.bold: true
        font.family: "Segoe UI"
        letterSpacing: 4
        color: toskPurple
        opacity: 0.8
        
        SequentialAnimation on opacity {
            NumberAnimation { from: 0.5; to: 1.0; duration: 1500 }
            NumberAnimation { from: 1.0; to: 0.5; duration: 1500 }
            loops: Animation.Infinite
            running: true
        }
    }
    
    // Efeito de celebração quando completo
    Rectangle {
        anchors.fill: parent
        radius: 15
        color: "transparent"
        border.width: 3
        border.color: toskCyan
        opacity: 0
        
        SequentialAnimation on opacity {
            NumberAnimation { from: 0; to: 1; duration: 300 }
            NumberAnimation { from: 1; to: 0; duration: 300 }
            loops: 3
            running: progressValue >= 1.0
        }
    }
    
    // Check mark gigante quando completo
    Text {
        anchors.centerIn: parent
        text: "✓"
        font.pixelSize: 120
        font.bold: true
        color: toskCyan
        opacity: 0
        visible: progressValue >= 1.0
        
        SequentialAnimation on opacity {
            NumberAnimation { from: 0; to: 1; duration: 500; easing.type: Easing.BackOut }
            running: progressValue >= 1.0
        }
        
        RotationAnimator {
            target: parent
            from: -45
            to: 0
            duration: 500
            easing.type: Easing.BackOut
            running: progressValue >= 1.0
        }
    }
}
