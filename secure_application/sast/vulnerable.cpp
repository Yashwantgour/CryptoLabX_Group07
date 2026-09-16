#include <iostream>
#include <cstring>
#include <cstdlib>

using namespace std;

void insecure_function(char* input) {
    char buffer[50];
    // Vulnerability 1: Buffer overflow using strcpy
    strcpy(buffer, input);
    cout << "Input copied: " << buffer << endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cout << "Usage: " << argv[0] << " <input>" << endl;
        return 1;
    }

    // Vulnerability 2: Hard-coded credentials
    char password[20] = "SecretPassword123!";
    
    // Vulnerability 3: gets() which is extremely dangerous
    char another_buffer[50];
    cout << "Enter some text: ";
    // gets(another_buffer); // Un-commenting would be very unsafe

    // Vulnerability 4: Unsafe command execution
    char command[100];
    sprintf(command, "echo %s", argv[1]);
    system(command);

    insecure_function(argv[1]);

    return 0;
}
