import QtQuick 2.15
import QtQuick.Controls 2.15

// Animação de Progresso - Pulso Radial
// Template 4: Ondas Concêntricas Expansivas

Rectangle {
    id: root
    width: 250
    height: 250
    color: "transparent"
    
    property real progressValue: 0.0
    property color pulseColor: "#3498db"
    property color centerColor: "#2ecc71"
    
    // Círculo central
    Rectangle {
        id: centerCircle
        anchors.centerIn: parent
        width: 60
        height: 60
        radius: 30
        color: centerColor
        
        SequentialAnimation on scale {
            NumberAnimation { from: 1.0; to: 1.2; duration: 600; easing.type: Easing.OutQuad }
            NumberAnimation { from: 1.2; to: 1.0; duration: 600; easing.type: Easing.InQuad }
            loops: Animation.Infinite
            running: true
        }
        
        // Ícone de check quando completo
        Text {
            anchors.centerIn: parent
            text: progressValue >= 1.0 ? "✓" : ""
            font.pixelSize: 36
            color: "white"
            font.bold: true
            font.family: "Segoe UI"
            
            SequentialAnimation on opacity {
                NumberAnimation { from: 0; to: 1; duration: 300 }
                running: progressValue >= 1.0
            }
        }
    }
    
    // Ondas concêntricas
    Repeater {
        model: 4
        Rectangle {
            id: wave
            anchors.centerIn: parent
            width: 80 + (index * 35)
            height: width
            radius: width / 2
            color: "transparent"
            border.color: pulseColor
            border.width: 3
            
            property real baseOpacity: 0.6 - (index * 0.15)
            opacity: baseOpacity * (1 - progressValue)
            
            SequentialAnimation {
                NumberAnimation {
                    target: wave
                    property: "scale"
                    from: 0.8
                    to: 1.3
                    duration: 1200 + (index * 200)
                    easing.type: Easing.OutQuad
                }
                NumberAnimation {
                    target: wave
                    property: "opacity"
                    from: baseOpacity
                    to: 0
                    duration: 400
                }
                loops: Animation.Infinite
                running: true
                startDelay: index * 300
            }
        }
    }
    
    // Anel de progresso externo
    Canvas {
        anchors.centerIn: parent
        width: 220
        height: 220
        
        property real currentProgress: 0
        
        NumberAnimation on currentProgress {
            from: 0
            to: progressValue
            duration: 500
            easing.type: Easing.OutCubic
            running: true
        }
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            
            // Anel de fundo
            ctx.strokeStyle = "#ecf0f1"
            ctx.lineWidth = 8
            ctx.beginPath()
            ctx.arc(110, 110, 100, 0, Math.PI * 2)
            ctx.stroke()
            
            // Anel de progresso
            ctx.strokeStyle = pulseColor
            ctx.lineWidth = 8
            ctx.lineCap = "round"
            ctx.beginPath()
            ctx.arc(110, 110, 100, -Math.PI/2, -Math.PI/2 + (currentProgress * Math.PI * 2))
            ctx.stroke()
        }
    }
    
    // Porcentagem central abaixo do círculo
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        text: Math.round(progressValue * 100) + "%"
        font.pixelSize: 28
        font.bold: true
        color: pulseColor
        font.family: "Segoe UI"
    }
}
