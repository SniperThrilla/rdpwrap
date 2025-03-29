#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 4096

/* str_replace()
 * -------------
 * Replaces all occurrences of a substring with a different string.
 * Used for replacing \r\n with \n in the output of the offset finder.
 */
void str_replace(char *target, const char *needle, const char *replacement)
{
    char buffer[1024] = { 0 };
    char *insert_point = &buffer[0];
    const char *tmp = target;
    size_t needle_len = strlen(needle);
    size_t repl_len = strlen(replacement);

    while (1) {
        const char *p = strstr(tmp, needle);

        // walked past last occurrence of needle; copy remaining part
        if (p == NULL) {
            strcpy(insert_point, tmp);
            break;
        }

        // copy part before needle
        memcpy(insert_point, tmp, p - tmp);
        insert_point += p - tmp;

        // copy replacement string
        memcpy(insert_point, replacement, repl_len);
        insert_point += repl_len;

        // adjust pointers, move on
        tmp = p + needle_len;
    }

    // write altered string back to target
    strcpy(target, buffer);
}

/* strndup()
 * ---------
 * A reimplementation of strndup, same behaviour as normal strndup,
 * however strndup is non-standard in C99.
 */
char *strndup(const char *s, size_t n) {
    char *dup = malloc(n + 1);
    if (dup) {
        strncpy(dup, s, n);
        dup[n] = '\0'; // null-terminate
    }
    return dup;
}

/* run_process()
 * ------------
 * Runs a process and outputs its stdout into the buffer.
 */
void *run_process(char *cmd, char** buffer) {
	HANDLE hRead, hWrite;
	SECURITY_ATTRIBUTES sa = {sizeof(SECURITY_ATTRIBUTES), NULL, TRUE};

	if (!CreatePipe(&hRead, &hWrite, &sa, 0)) {
		fprintf(stderr, "FATAL: Could not create pipe.\n");
		exit(1);
	}

	STARTUPINFO si = {sizeof(STARTUPINFO)};
	PROCESS_INFORMATION pi;
	si.dwFlags = STARTF_USESTDHANDLES;
	si.hStdOutput = hWrite;
	si.hStdError = hWrite;

	if (!CreateProcess(NULL, cmd, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi)) {
		fprintf(stderr, "FATAL: Could not create process.\n");
		CloseHandle(hRead);
		CloseHandle(hWrite);
		exit(1);
	}

	CloseHandle(hWrite);

	DWORD bytesRead;
	while (ReadFile(hRead, *buffer, BUFFER_SIZE-1, &bytesRead, NULL) && bytesRead > 0) {
		(*buffer)[bytesRead] = '\0';
	}

	CloseHandle(hRead);
	CloseHandle(pi.hProcess);
	CloseHandle(pi.hThread);
}

/* generate_ini_contents()
 * -----------------------
 * Uses boilerplate rdpwrap.ini contents from sebaxakerhtc
 * and combines it with the specific offsets for your windows
 * build.
 */
char *generate_ini_contents() {
	char *mainSection = "[Main]\n\
Updated=2025-01-01\n\
LogFile=\\rdpwrap.txt\n\
SLPolicyHookNT60=1\n\
SLPolicyHookNT61=1\n";

	char *SLPolicySection = "[SLPolicy]\n\
TerminalServices-RemoteConnectionManager-AllowRemoteConnections=1\n\
TerminalServices-RemoteConnectionManager-AllowMultipleSessions=1\n\
TerminalServices-RemoteConnectionManager-AllowAppServerMode=1\n\
TerminalServices-RemoteConnectionManager-AllowMultimon=1\n\
TerminalServices-RemoteConnectionManager-MaxUserSessions=0\n\
TerminalServices-RemoteConnectionManager-ce0ad219-4670-4988-98fb-89b14c2f072b-MaxSessions=0\n\
TerminalServices-RemoteConnectionManager-45344fe7-00e6-4ac6-9f01-d01fd4ffadfb-MaxSessions=2\n\
TerminalServices-RDP-7-Advanced-Compression-Allowed=1\n\
TerminalServices-RemoteConnectionManager-45344fe7-00e6-4ac6-9f01-d01fd4ffadfb-LocalOnly=0\n\
TerminalServices-RemoteConnectionManager-8dc86f1d-9969-4379-91c1-06fe1dc60575-MaxSessions=1000\n\
TerminalServices-DeviceRedirection-Licenses-TSEasyPrintAllowed=1\n\
TerminalServices-DeviceRedirection-Licenses-PnpRedirectionAllowed=1\n\
TerminalServices-DeviceRedirection-Licenses-TSMFPluginAllowed=1\n\
TerminalServices-RemoteConnectionManager-UiEffects-DWMRemotingAllowed=1\n";

	char *PatchCodesSection = "[PatchCodes]\n\
nop=90\n\
Zero=00\n\
nop_3=909090\n\
nop_4=90909090\n\
nop_7=90909090909090\n\
nopjmp=90E9\n\
jmpshort=EB\n\
mov_eax_1_nop_1=B80100000090\n\
mov_eax_1_nop_2=B8010000009090\n\
pop_eax_add_esp_12_nop_2=5883C40C9090\n\
CDefPolicy_Query_eax_esi=B80001000089862003000090\n\
CDefPolicy_Query_edx_ecx=BA000100008991200300005E90\n\
CDefPolicy_Query_eax_rdi=B80001000089873806000090\n\
CDefPolicy_Query_eax_rdi_jmp=B80001000089873806000090EB\n\
; CDefPolicy_Query_eax_rdi_jmp=B800010000898738060000EB0D\n\
CDefPolicy_Query_eax_ecx=B80001000089812403000090\n\
; CDefPolicy_Query_eax_ecx=B80001000089812003000090\n\
CDefPolicy_Query_eax_ecx_jmp=B800010000898120030000EB0E\n\
CDefPolicy_Query_eax_rcx=B80001000089813806000090\n\
CDefPolicy_Query_eax_rcx_jmp=B80001000089813806000090EB\n\
CDefPolicy_Query_edi_rcx=BF0001000089B938060000909090\n";

	char *SLInitSection = "[SLInit]\n\
bServerSku=1\n\
bRemoteConnAllowed=1\n\
bFUSEnabled=1\n\
bAppServerAllowed=1\n\
bMultimonAllowed=1\n\
lMaxUserSessions=0\n\
ulMaxDebugSessions=0\n\
bInitialized=1\n";

	char *excessSection = "[10.0.27813.1000-SLInit]\n\
bInitialized.x64      =129EE8\n\
bServerSku.x64        =129EEC\n\
lMaxUserSessions.x64  =129EF0\n\
bAppServerAllowed.x64 =129EF8\n\
bRemoteConnAllowed.x64=129F00\n\
bMultimonAllowed.x64  =129F04\n\
ulMaxDebugSessions.x64=129F0C\n\
bFUSEnabled.x64       =129F10";

	// Generate custom offsets.
	char *mainValues = malloc(4096 * sizeof(char));
	memset(mainValues, 0, 4096 * sizeof(char));
        run_process("OffsetFinder\\RDPWrapOffsetFinder.exe", &mainValues);
	char *slinitValues = strstr(mainValues, "\r\n\r\n")+2;
	char *regularValues = strndup(mainValues, slinitValues-mainValues);
	str_replace(slinitValues, "\r\n" , "\n");
	str_replace(regularValues, "\r\n", "\n");


	// Build the contents of the ini file.
	char *result = malloc(8192);
	result[0] = '\0';
	strcat(result, mainSection);
	strcat(result, "\n");
	strcat(result, SLPolicySection);
	strcat(result, "\n");
	strcat(result, PatchCodesSection);
	strcat(result, "\n");
	strcat(result, regularValues);
	strcat(result, "\n");
	strcat(result, SLInitSection);
	strcat(result, slinitValues);
	strcat(result, "\n");
	strcat(result, excessSection);
	
	return result;
}

/* prepare_rdp()
 * -------------
 * Renames the old rdpwrap.ini to old.ini and stop Remote Desktop Services.
 */
void prepare_rdp() {
	system("net stop TermService");
	system("rename \"C:\\Program Files\\RDP Wrapper\\rdpwrap.ini\" old.ini");
}

/* create_ini()
 * ------------
 * Create the file and write to it.
 */
void create_ini(char* config) {
	FILE *file = fopen("C:\\Program Files\\RDP Wrapper\\rdpwrap.ini", "w");

	if (file == NULL) {
		fprintf(stderr, "FATAL: Could not create new rdpwrap.ini file!\n");
		exit(1);
	}

	fprintf(file, "%s", config);
	fclose(file);
}

/* finalise()
 * ----------
 * Turn on the Remote Desktop Services service.
 */
void finalise() {
	system("net start TermService");
}

int main(int argc, char** argv) {
	printf("Calculating your offset values...\n");
	char *config = generate_ini_contents();
	printf("Successfully generated contents for rdpwrap.ini!\n");
	printf("Now turning off Remote Desktop Services and renaming your old rdpwrap.ini file!\n");
	prepare_rdp();
	create_ini(config);
	finalise();
}
