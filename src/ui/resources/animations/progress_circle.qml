import QtQuick 2.15
import QtQuick.Controls 2.15

// Animação de Progresso - Círculo Giratório
// Template 1: Spinner Circular Moderno

Rectangle {
    id: root
    width: 200
    height: 200
    color: "transparent"
    
    property real progressValue: 0.0
    property color primaryColor: "#3498db"
    property color secondaryColor: "#2ecc71"
    
    // Círculo de fundo
    Canvas {
        anchors.centerIn: parent
        width: 160
        height: 160
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            ctx.strokeStyle = "#ecf0f1"
            ctx.lineWidth = 12
            ctx.beginPath()
            ctx.arc(80, 80, 70, 0, Math.PI * 2)
            ctx.stroke()
        }
    }
    
    // Círculo de progresso animado
    Canvas {
        id: progressCircle
        anchors.centerIn: parent
        width: 160
        height: 160
        
        property real sweepAngle: 0
        
        NumberAnimation on sweepAngle {
            from: 0
            to: 360
            duration: 1500
            loops: Animation.Infinite
            running: true
        }
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            ctx.strokeStyle = primaryColor
            ctx.lineWidth = 12
            ctx.lineCap = "round"
            ctx.beginPath()
            ctx.arc(80, 80, 70, -Math.PI/2, -Math.PI/2 + (sweepAngle * Math.PI / 180))
            ctx.stroke()
        }
    }
    
    // Texto de porcentagem central
    Text {
        anchors.centerIn: parent
        text: Math.round(progressValue * 100) + "%"
        font.pixelSize: 32
        font.bold: true
        color: primaryColor
        font.family: "Segoe UI"
        
        SequentialAnimation on scale {
            NumberAnimation { to: 1.1; duration: 500 }
            NumberAnimation { to: 1.0; duration: 500 }
            loops: Animation.Infinite
            running: true
        }
    }
}
