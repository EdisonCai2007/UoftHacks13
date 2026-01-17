# buddy.py - PyObjC version for macOS
from Cocoa import (NSWindow, NSBackingStoreBuffered, NSBorderlessWindowMask,
                   NSColor, NSImage, NSImageView, NSMakeRect, NSApplication,
                   NSApp, NSTimer, NSObject, NSTextField, NSFont)
from AppKit import (NSWindowCollectionBehaviorCanJoinAllSpaces, 
                    NSWindowCollectionBehaviorStationary,
                    NSTextAlignmentCenter)
import os
import math
import objc
import threading
from flask import Flask, request, jsonify

# ========================
# CONFIGURATION
# ========================
IMAGE_PATH_1 = os.path.expanduser("../assets/moose1.png")
IMAGE_PATH_2 = os.path.expanduser("../assets/moose2.png")
START_X = 1000
MOVE_STEP = 6
LEAP_HEIGHT = 40

# Screen dimensions - set to your monitor size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_RIGHT_EDGE = SCREEN_WIDTH - 150

# Window size - just big enough for moose and speech bubble
WINDOW_WIDTH = 150
WINDOW_HEIGHT = 200

# Position at bottom of screen (window coordinates, not content view)
BASE_Y = 120

# ========================
# FLASK SERVER
# ========================
app = Flask(__name__)
controller = None  # Will be set after controller is created

@app.route('/data', methods=['POST'])
def receive_data():
    global controller
    data = request.json
    if data and controller:
        animation = data.get("animation")
        message = data.get("message", "")
        
        # Update controller state
        controller.current_animation = animation
        controller.current_message = message
        controller.updateBubble()
            
    return jsonify({"status": "ok"}), 200

def run_server():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

class BuddyController(NSObject):
    def init(self):
        self = objc.super(BuddyController, self).init()
        if self is None:
            return None
        
        self.x = START_X
        self.y = BASE_Y
        self.direction = -1
        self.leap_progress = 0
        self.current_animation = "walk"
        self.current_message = ""
        
        # Create transparent window - small size for moose
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(START_X, BASE_Y, WINDOW_WIDTH, WINDOW_HEIGHT),
            NSBorderlessWindowMask,
            NSBackingStoreBuffered,
            False
        )
        
        # Make window transparent
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setOpaque_(False)
        self.window.setHasShadow_(False)
        self.window.setLevel_(3)
        self.window.setIgnoresMouseEvents_(True)  # Let clicks pass through transparent areas
        
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces |
            NSWindowCollectionBehaviorStationary
        )
        
        # Create message label (speech bubble) - positioned within small window
        self.messageLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 110, 130, 80))
        self.messageLabel.setStringValue_("")
        self.messageLabel.setEditable_(False)
        self.messageLabel.setBordered_(True)
        self.messageLabel.setDrawsBackground_(True)
        self.messageLabel.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 1.0, 0.99, 1.0))
        self.messageLabel.setTextColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.1, 0.1, 0.1, 1.0))
        self.messageLabel.setFont_(NSFont.boldSystemFontOfSize_(10))
        self.messageLabel.setAlignment_(NSTextAlignmentCenter)
        self.messageLabel.setHidden_(True)
        self.window.contentView().addSubview_(self.messageLabel)
        
        # Load images
        self.image1_right = NSImage.alloc().initWithContentsOfFile_(IMAGE_PATH_1)
        self.image2_right = NSImage.alloc().initWithContentsOfFile_(IMAGE_PATH_2)
        
        # Create flipped versions for left movement
        self.image1_left = self.flipImageHorizontally_(self.image1_right)
        self.image2_left = self.flipImageHorizontally_(self.image2_right)
        
        self.imageView = NSImageView.alloc().initWithFrame_(NSMakeRect(25, 0, 100, 100))
        self.imageView.setImage_(self.image2_right)
        
        # Add click handler to close program
        from Cocoa import NSClickGestureRecognizer
        clickRecognizer = NSClickGestureRecognizer.alloc().initWithTarget_action_(self, 'handleClick:')
        self.imageView.addGestureRecognizer_(clickRecognizer)
        
        self.window.contentView().addSubview_(self.imageView)
        self.window.makeKeyAndOrderFront_(None)
        
        # Start timer
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.05, self, 'moveBuddy:', None, True
        )
        
        return self
    
    def handleClick_(self, recognizer):
        """Handle clicks on the buddy - quit the program"""
        print("👋 Buddy clicked - exiting program...")
        NSApp.terminate_(None)
        import sys
        sys.exit(0)
    
    def updateBubble(self):
        """Update the message bubble visibility"""
        if self.current_animation == "talk" and self.current_message.strip():
            self.messageLabel.setStringValue_(self.current_message)
            self.messageLabel.setHidden_(False)
        else:
            self.messageLabel.setHidden_(True)
    
    def flipImageHorizontally_(self, image):
        """Flip an NSImage horizontally"""
        from Cocoa import NSAffineTransform, NSCompositeCopy
        
        size = image.size()
        flipped = NSImage.alloc().initWithSize_(size)
        
        flipped.lockFocus()
        
        # Create transform for horizontal flip
        transform = NSAffineTransform.transform()
        transform.translateXBy_yBy_(size.width, 0)
        transform.scaleXBy_yBy_(-1.0, 1.0)
        transform.concat()
        
        # Draw the original image with the transform applied
        image.drawAtPoint_fromRect_operation_fraction_(
            (0, 0),
            NSMakeRect(0, 0, size.width, size.height),
            NSCompositeCopy,
            1.0
        )
        
        flipped.unlockFocus()
        return flipped
    
    def rotateImage_byDegrees_(self, image, degrees):
        """Rotate an NSImage by the specified degrees"""
        from Cocoa import NSAffineTransform, NSCompositeCopy
        
        size = image.size()
        rotated = NSImage.alloc().initWithSize_(size)
        
        rotated.lockFocus()
        
        # Create transform for rotation
        transform = NSAffineTransform.transform()
        # Move to center, rotate, move back
        transform.translateXBy_yBy_(size.width / 2, size.height / 2)
        transform.rotateByDegrees_(degrees)
        transform.translateXBy_yBy_(-size.width / 2, -size.height / 2)
        transform.concat()
        
        # Draw the original image with the transform applied
        image.drawAtPoint_fromRect_operation_fraction_(
            (0, 0),
            NSMakeRect(0, 0, size.width, size.height),
            NSCompositeCopy,
            1.0
        )
        
        rotated.unlockFocus()
        return rotated
    
    def moveBuddy_(self, timer):
        """Timer callback - note the underscore for PyObjC selector"""
        if self.current_animation == "walk":
            # Move horizontally
            self.x += MOVE_STEP * self.direction
            if self.x < 0 or self.x > SCREEN_RIGHT_EDGE:
                self.direction *= -1
            
            # Leap animation with smoother progression
            self.leap_progress += 0.10  # Faster gallop up/down
            if self.leap_progress > 1:
                self.leap_progress = 0
            
            # Sine wave creates the arc/bounce effect
            y_offset = int(math.sin(self.leap_progress * math.pi) * LEAP_HEIGHT)
            current_y = BASE_Y + y_offset
            
            # Calculate rotation angle based on leap progress
            rotation_angle = (self.leap_progress - 0.5) * 50
            
            # Move the entire window
            self.window.setFrameOrigin_(NSMakeRect(self.x, current_y, WINDOW_WIDTH, WINDOW_HEIGHT).origin)
            
            # Select base image and apply rotation - matches old tkinter logic
            if current_y != BASE_Y:  # When not on ground (jumping)
                base_img = self.image1_right if self.direction == 1 else self.image1_left
                rotated_img = self.rotateImage_byDegrees_(base_img, rotation_angle)
                self.imageView.setImage_(rotated_img)
            else:
                # Use standing image when on ground
                img = self.image2_right if self.direction == 1 else self.image2_left
                self.imageView.setImage_(img)
        else:
            # Standing still (talk mode)
            self.window.setFrameOrigin_(NSMakeRect(self.x, BASE_Y, WINDOW_WIDTH, WINDOW_HEIGHT).origin)
            img = self.image2_right if self.direction == 1 else self.image2_left
            self.imageView.setImage_(img)

# Create application and controller
app_ns = NSApplication.sharedApplication()
controller = BuddyController.alloc().init()

# Start Flask server in background thread
threading.Thread(target=run_server, daemon=True).start()

# Handle Ctrl+C gracefully
import signal
import sys

def signal_handler(sig, frame):
    print('\n👋 Buddy exiting...')
    app_ns.terminate_(None)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("Buddy is running! Press Ctrl+C to quit.")

# Run app
app_ns.run()
